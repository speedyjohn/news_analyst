import argparse
import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.core.db import session_scope
from app.core.errors import AppError
from app.llm.factory import build_llm
from app.models import News, Source
from app.services import closure, ingestion, sources as sources_service

log = logging.getLogger(__name__)


def run(hours: int = 24, only: str | None = None) -> dict:
    until = datetime.now(UTC)
    since = until - timedelta(hours=hours)

    with session_scope() as session:
        sources_service.sync_from_yaml(session)

    try:
        llm = build_llm()
    except AppError as exc:
        log.warning("%s — прогон идёт без оценки важности и без закрытия вопросов", exc.message)
        llm = None

    with session_scope() as session:
        result = ingestion.run_daily(session, llm, since=since, until=until, only=only)
        if llm is None:
            result["closed_questions"] = 0
        else:
            fresh = list(session.scalars(select(News).where(News.id.in_(result["saved_ids"]))))
            result["closed_questions"] = closure.run(session, llm, fresh)

    log.info("Суточный прогон завершён: %s", result)
    return result


def dry_run(hours: int, only: str | None) -> None:
    since = datetime.now(UTC) - timedelta(hours=hours)
    entries = {entry["code"]: entry for entry in sources_service.load_yaml()}

    with session_scope() as session:
        query = select(Source).where(Source.enabled.is_(True))
        if only:
            query = select(Source).where(Source.code == only)
        sources = list(session.scalars(query.order_by(Source.priority)))

    for source in sources:
        entry = entries.get(source.code, {})
        print("=" * 78)
        print(f"{source.code} — {source.name}")
        try:
            parser = ingestion.build_parser(
                parser=source.parser,
                code=source.code,
                url=source.url,
                feed_url=source.feed_url,
                **sources_service.parser_options(entry),
            )
            articles = parser.fetch(since)
        except Exception as exc:  # noqa: BLE001
            print(f"  ОШИБКА: {type(exc).__name__}: {exc}")
            continue

        print(f"  материалов за окно: {len(articles)}")
        for article in articles[:5]:
            print(f"  · {article.published_at:%Y-%m-%d %H:%M} UTC  {article.title[:70]}")
            print(f"    {article.url[:90]}")
            print(f"    текст: {len(article.full_text)} симв.")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(description="Суточный прогон сбора новостей")
    parser.add_argument("--source", help="код источника из sources.yaml")
    parser.add_argument("--hours", type=int, default=24, help="ширина окна в часах")
    parser.add_argument("--dry-run", action="store_true", help="показать материалы, ничего не сохраняя")
    args = parser.parse_args()

    if args.dry_run:
        dry_run(args.hours, args.source)
    else:
        print(run(hours=args.hours, only=args.source))


if __name__ == "__main__":
    main()
