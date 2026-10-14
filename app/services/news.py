from datetime import UTC, date, datetime, time, timedelta

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.core.errors import NotFound
from app.models import STATUS_CLOSED, News, Question
from app.services import ranking

PAGE_SIZE = 20
TOP_SIZES = (3, 5, 10)


def day_bounds(day: date, tz_offset_hours: int = 5) -> tuple[datetime, datetime]:
    start_local = datetime.combine(day, time.min)
    start_utc = start_local.replace(tzinfo=UTC) - timedelta(hours=tz_offset_hours)
    return start_utc, start_utc + timedelta(days=1)


REGIONS: dict[str, tuple[str, ...]] = {
    "kz": ("KZ",),
    "cis": ("RU", "BY", "UZ", "KG", "TJ", "AM", "AZ", "MD", "TM", "CIS", "EAEU"),
    "europe": (
        "EU", "DE", "FR", "IT", "ES", "PL", "NL", "BE", "AT", "CH", "SE", "FI", "NO", "DK",
        "CZ", "SK", "HU", "RO", "BG", "GR", "PT", "IE", "LT", "LV", "EE", "UK", "GB",
    ),
    "america": ("US", "CA", "MX", "BR", "AR", "CL", "CO", "PE"),
}


def _base_query(day: date | None, category: str | None, region: str | None) -> Select:
    query = select(News)
    if day is not None:
        since, until = day_bounds(day)
        query = query.where(News.published_at >= since, News.published_at < until)
    if category in ranking.CATEGORIES:
        query = query.where(News.category == category)
    if region in REGIONS:
        query = query.where(News.country.in_(REGIONS[region]))
    return query


def question_counts(session: Session, news_ids: list[int]) -> dict[int, tuple[int, int]]:
    if not news_ids:
        return {}
    rows = session.execute(
        select(
            Question.news_id,
            func.count(Question.id),
            func.count(Question.id).filter(Question.status == STATUS_CLOSED),
        )
        .where(Question.news_id.in_(news_ids))
        .group_by(Question.news_id)
    ).all()
    return {news_id: (closed, total) for news_id, total, closed in rows}


def feed(
    session: Session,
    *,
    day: date | None = None,
    top: int | None = None,
    category: str | None = None,
    region: str | None = None,
    page: int = 1,
) -> dict:
    query = _base_query(day, category, region)

    if top in TOP_SIZES:
        items = list(
            session.scalars(
                query.where(News.importance_score.is_not(None))
                .order_by(News.importance_score.desc(), News.published_at.desc())
                .limit(top)
            )
        )
        total = len(items)
    else:
        total = session.scalar(select(func.count()).select_from(query.subquery())) or 0
        page = max(1, page)
        items = list(
            session.scalars(
                query.order_by(News.published_at.desc())
                .offset((page - 1) * PAGE_SIZE)
                .limit(PAGE_SIZE)
            )
        )

    return {
        "items": items,
        "counts": question_counts(session, [n.id for n in items]),
        "total": total,
        "page": page,
        "page_size": PAGE_SIZE,
    }


def get_news(session: Session, news_id: int) -> News:
    news = session.get(News, news_id)
    if news is None:
        raise NotFound("Новость не найдена")
    return news


def available_dates(session: Session, limit: int = 30) -> list[date]:
    rows = session.execute(
        select(func.date(News.published_at)).group_by(func.date(News.published_at))
        .order_by(func.date(News.published_at).desc()).limit(limit)
    ).scalars().all()
    return [r if isinstance(r, date) else date.fromisoformat(str(r)) for r in rows]
