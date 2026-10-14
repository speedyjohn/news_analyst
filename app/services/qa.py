import json
import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import ModerationRejected, NotFound, RateLimited, ValidationError
from app.llm.base import LLMProvider
from app.llm.prompts import load_prompt
from app.models import STATUS_OPEN, News, Question, User
from app.services import textutil
from app.services.llm_gateway import ask_json

log = logging.getLogger(__name__)

MAX_QUESTION_LEN = 300
CONTEXT_LIMIT = 10


def check_limits(session: Session, user: User) -> None:
    now = datetime.now(UTC)
    per_hour = session.scalar(
        select(func.count(Question.id)).where(
            Question.user_id == user.id, Question.created_at >= now - timedelta(hours=1)
        )
    )
    if per_hour >= settings.questions_per_hour:
        raise RateLimited(f"Не больше {settings.questions_per_hour} вопросов в час. Попробуйте позже.")

    per_day = session.scalar(
        select(func.count(Question.id)).where(
            Question.user_id == user.id, Question.created_at >= now - timedelta(days=1)
        )
    )
    if per_day >= settings.questions_per_day:
        raise RateLimited(f"Не больше {settings.questions_per_day} вопросов в сутки. Попробуйте завтра.")


def moderate(session: Session, llm: LLMProvider, news: News, text: str) -> None:
    result = ask_json(
        session,
        llm,
        task="question_moderation",
        system=load_prompt("question_moderation"),
        user=f"Новость: {news.title}\n\n{(news.summary or news.full_text or '')[:2000]}\n\nВопрос: {text}",
        schema={"allowed": "boolean", "reason": "string|null"},
        max_tokens=300,
    )
    if not result.get("allowed"):
        raise ModerationRejected(
            result.get("reason") or "Вопрос отклонён модерацией. Переформулируйте его по содержанию новости."
        )


def related_news(session: Session, news: News, text: str, limit: int = CONTEXT_LIMIT) -> list[News]:
    query_words = textutil.significant_words(f"{news.title} {text}")
    candidates = session.scalars(
        select(News)
        .where(News.id != news.id, News.published_at >= datetime.now(UTC) - timedelta(days=90))
        .order_by(News.published_at.desc())
        .limit(300)
    ).all()

    scored = [
        (len(query_words & textutil.significant_words(f"{c.title} {c.summary or ''}")), c)
        for c in candidates
    ]
    best = [c for score, c in sorted(scored, key=lambda p: -p[0]) if score > 0][:limit]
    return [news, *best]


def _context_block(items: list[News]) -> str:
    parts = []
    for index, item in enumerate(items, start=1):
        body = (item.summary or item.full_text or "")[:1500]
        parts.append(
            f"[{index}] {item.title}\n"
            f"Источник: {item.source.name} ({item.url})\n"
            f"Дата: {item.published_at:%Y-%m-%d}\n"
            f"{body}"
        )
    return "\n\n".join(parts)


def build_answer(session: Session, llm: LLMProvider, question: Question) -> str:
    items = related_news(session, question.news, question.text)
    result = ask_json(
        session,
        llm,
        task="question_answer",
        system=load_prompt("question_answer"),
        user=f"Материалы:\n\n{_context_block(items)}\n\nВопрос пользователя: {question.text}",
        schema={
            "facts": [{"text": "string", "source_id": "integer|null"}],
            "assessment": "string|null",
        },
        max_tokens=1500,
    )

    facts = []
    for fact in result.get("facts") or []:
        text = (fact.get("text") or "").strip()
        if not text:
            continue
        source = _resolve_source(items, fact.get("source_id"))
        if source is None and len(facts) > 0:
            continue
        facts.append({"text": text, "source": source})

    if not facts:
        facts = [{"text": "В официальных источниках информации по этому вопросу пока нет", "source": None}]

    return json.dumps(
        {"facts": facts, "assessment": (result.get("assessment") or "").strip() or None},
        ensure_ascii=False,
    )


def _resolve_source(items: list[News], source_id: object) -> dict | None:
    try:
        index = int(source_id) - 1
    except (TypeError, ValueError):
        return None
    if 0 <= index < len(items):
        item = items[index]
        return {"news_id": item.id, "title": item.source.name, "url": item.url}
    return None


def ask(session: Session, llm: LLMProvider, *, user: User, news_id: int, text: str) -> Question:
    text = (text or "").strip()
    if not text:
        raise ValidationError("Вопрос не может быть пустым")
    if len(text) > MAX_QUESTION_LEN:
        raise ValidationError(f"Вопрос длиннее {MAX_QUESTION_LEN} символов")

    news = session.get(News, news_id)
    if news is None:
        raise NotFound("Новость не найдена")

    check_limits(session, user)
    moderate(session, llm, news, text)

    question = Question(user_id=user.id, news_id=news.id, text=text, status=STATUS_OPEN)
    session.add(question)
    session.flush()

    try:
        question.ai_answer = build_answer(session, llm, question)
    except Exception:
        log.exception("Не удалось сгенерировать ответ на вопрос %s", question.id)

    return question
