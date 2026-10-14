import logging
from typing import Any

from sqlalchemy.orm import Session

from app.llm.base import LLMProvider
from app.llm.prompts import load_prompt
from app.models import News
from app.services.llm_gateway import ask_json

log = logging.getLogger(__name__)

CATEGORY_POLITICS = "politics"
CATEGORY_ECONOMY = "economy"
CATEGORY_BUSINESS = "business"
CATEGORY_OTHER = "other"
CATEGORIES = (CATEGORY_POLITICS, CATEGORY_ECONOMY, CATEGORY_BUSINESS, CATEGORY_OTHER)
CATEGORY_LEGACY = "political_economic"

_SCHEMA = {
    "summary": "string",
    "category": "politics | economy | business | other",
    "importance_score": "integer 0-100",
    "importance_reason": "string",
}


def _payload(news: News) -> str:
    body = (news.full_text or "")[:8000]
    return (
        f"Источник: {news.source.name}\n"
        f"Страна: {news.country}\n"
        f"Дата публикации: {news.published_at:%Y-%m-%d %H:%M} UTC\n"
        f"Заголовок: {news.title}\n\n"
        f"Текст:\n{body if body else '(источник отдал только заголовок)'}"
    )


def analyze(session: Session, llm: LLMProvider, news: News) -> News:
    try:
        data: dict[str, Any] = ask_json(
            session,
            llm,
            task="news_analysis",
            system=load_prompt("news_analysis"),
            user=_payload(news),
            schema=_SCHEMA,
            max_tokens=800,
            user_facing=False,
        )
    except Exception:
        log.exception("Не удалось оценить новость %s", news.url)
        news.category = news.category or CATEGORY_OTHER
        return news

    news.summary = (data.get("summary") or "").strip() or None
    category = data.get("category")
    news.category = category if category in CATEGORIES else CATEGORY_OTHER
    news.importance_score = _clamp(data.get("importance_score"))
    news.importance_reason = (data.get("importance_reason") or "").strip() or None
    return news


def _clamp(value: Any) -> int | None:
    try:
        return max(0, min(100, int(value)))
    except (TypeError, ValueError):
        return None
