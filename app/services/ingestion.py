import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.llm.base import LLMProvider
from app.models import IngestionRun, News, Source
from app.parsers.base import RawArticle
from app.parsers.registry import build_parser
from app.services import ranking, sources as sources_service

log = logging.getLogger(__name__)


def collect_source(
    session: Session,
    source: Source,
    options: dict,
    *,
    since: datetime,
    until: datetime,
) -> tuple[list[News], IngestionRun]:
    run = IngestionRun(source_code=source.code, started_at=datetime.now(UTC))
    session.add(run)
    saved: list[News] = []

    try:
        parser = build_parser(
            parser=source.parser,
            code=source.code,
            url=source.url,
            feed_url=source.feed_url,
            **options,
        )
        articles = parser.fetch(since)
        fresh = [a for a in articles if a.published_at <= until][: settings.ingestion_max_items]
        run.items_found = len(fresh)

        for article in fresh:
            news = _save_article(session, source, article)
            if news is not None:
                saved.append(news)
        run.items_saved = len(saved)
        run.status = "ok"
        source.last_success_at = datetime.now(UTC)
    except Exception as exc:  # noqa: BLE001
        log.exception("Источник %s упал", source.code)
        run.status = "failed"
        run.error = f"{type(exc).__name__}: {exc}"[:2000]
    finally:
        run.finished_at = datetime.now(UTC)
        session.flush()

    return saved, run


def _save_article(session: Session, source: Source, article: RawArticle) -> News | None:
    existing = session.scalar(select(News).where(News.content_hash == article.content_hash))
    if existing is not None:
        if source.priority < existing.source.priority:
            log.info(
                "Дубль %s: %s приоритетнее %s, но запись уже создана — оставляем как есть",
                article.title[:60],
                source.code,
                existing.source.code,
            )
        return None
    if session.scalar(select(News).where(News.url == article.url)) is not None:
        return None

    news = News(
        source_id=source.id,
        title=article.title[:700],
        full_text=article.full_text,
        url=article.url[:1000],
        published_at=article.published_at,
        language=article.language,
        country=source.country,
        content_hash=article.content_hash,
    )
    session.add(news)
    session.flush()
    return news


# добираем новости, сохранённые без оценки (например, когда не было ключа)
BACKFILL_DAYS = 7


def _to_analyze(session: Session, fresh: list[News]) -> list[News]:
    seen = {news.id for news in fresh}
    pending = session.scalars(
        select(News)
        .where(
            or_(News.importance_score.is_(None), News.category == ranking.CATEGORY_LEGACY),
            News.published_at >= datetime.now(UTC) - timedelta(days=BACKFILL_DAYS),
        )
        .order_by(News.published_at.desc())
    ).all()
    return [*fresh, *(news for news in pending if news.id not in seen)]


def run_daily(
    session: Session,
    llm: LLMProvider | None,
    *,
    since: datetime | None = None,
    until: datetime | None = None,
    only: str | None = None,
) -> dict:
    until = until or datetime.now(UTC)
    since = since or (until - timedelta(days=1))
    log.info("Прогон за окно %s — %s", since, until)

    entries = {entry["code"]: entry for entry in sources_service.load_yaml()}
    all_new: list[News] = []
    runs: list[IngestionRun] = []

    query = select(Source).where(Source.enabled.is_(True))
    if only:
        query = select(Source).where(Source.code == only)

    for source in session.scalars(query.order_by(Source.priority)):
        options = sources_service.parser_options(entries.get(source.code, {}))
        saved, run = collect_source(session, source, options, since=since, until=until)
        all_new.extend(saved)
        runs.append(run)
        session.commit()

    if llm is not None:
        for news in _to_analyze(session, all_new):
            ranking.analyze(session, llm, news)
            session.commit()
    else:
        log.warning("LLM недоступен: %d новостей сохранены без оценки важности", len(all_new))

    result = {
        "window": {"since": since.isoformat(), "until": until.isoformat()},
        "sources": len(runs),
        "failed": [r.source_code for r in runs if r.status == "failed"],
        "saved": len(all_new),
        "saved_ids": [n.id for n in all_new],
    }
    log.info("Прогон завершён: %s", result)
    return result


def refetch_texts(session: Session, *, only: str | None = None) -> int:
    entries = {entry["code"]: entry for entry in sources_service.load_yaml()}
    query = select(Source)
    if only:
        query = query.where(Source.code == only)

    updated = 0
    for source in session.scalars(query):
        parser = build_parser(
            parser=source.parser,
            code=source.code,
            url=source.url,
            feed_url=source.feed_url,
            **sources_service.parser_options(entries.get(source.code, {})),
        )
        for news in session.scalars(select(News).where(News.source_id == source.id)):
            text = parser.page_text(news.url)
            if text and text != news.full_text:
                news.full_text = text
                updated += 1
        session.commit()
        log.info("%s: обновлено текстов — %d", source.code, updated)
    return updated
