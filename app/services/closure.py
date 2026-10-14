import logging
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.llm.base import LLMProvider
from app.llm.prompts import load_prompt
from app.models import STATUS_CLOSED, STATUS_OPEN, News, Question
from app.services import notifier, textutil
from app.services.llm_gateway import ask_json

log = logging.getLogger(__name__)

PREFILTER_MIN_OVERLAP = 2
MAX_CANDIDATES_PER_NEWS = 12


def candidates(session: Session, news: News) -> list[Question]:
    open_questions = session.scalars(select(Question).where(Question.status == STATUS_OPEN)).all()
    news_words = textutil.significant_words(f"{news.title} {news.summary or ''} {news.full_text or ''}")

    scored = [(len(news_words & textutil.significant_words(q.text)), q) for q in open_questions]
    passing = [(score, q) for score, q in scored if score >= PREFILTER_MIN_OVERLAP]
    return [q for _, q in sorted(passing, key=lambda p: -p[0])][:MAX_CANDIDATES_PER_NEWS]


def check_news(session: Session, llm: LLMProvider, news: News) -> list[Question]:
    batch = candidates(session, news)
    if not batch:
        return []

    listing = "\n".join(f"[{q.id}] {q.text}" for q in batch)
    body = (news.full_text or news.summary or "")[:6000]
    try:
        verdicts = ask_json(
            session,
            llm,
            task="question_closure",
            system=load_prompt("question_closure"),
            user=(
                f"Публикация: {news.title}\nИсточник: {news.source.name}\n"
                f"Дата: {news.published_at:%Y-%m-%d}\n\n{body}\n\n"
                f"Открытые вопросы:\n{listing}"
            ),
            schema=[{"question_id": "integer", "closes": "boolean", "official_answer": "string|null"}],
            max_tokens=1500,
            user_facing=False,
        )
    except Exception:
        log.exception("Проверка закрытия для новости %s не удалась", news.id)
        return []

    by_id = {q.id: q for q in batch}
    closed: list[Question] = []
    for verdict in verdicts if isinstance(verdicts, list) else []:
        question = by_id.get(verdict.get("question_id"))
        answer = (verdict.get("official_answer") or "").strip()
        if question is None or not verdict.get("closes") or not answer:
            continue
        if question.status == STATUS_CLOSED:
            continue
        question.status = STATUS_CLOSED
        question.official_answer = answer
        # объект, а не id - иначе notifier не увидит новость
        question.closing_news = news
        question.closed_at = datetime.now(UTC)
        closed.append(question)

    session.flush()
    return closed


def run(session: Session, llm: LLMProvider, fresh_news: list[News]) -> int:
    total = 0
    for news in fresh_news:
        for question in check_news(session, llm, news):
            session.commit()
            notifier.notify_question_closed(question)
            total += 1
    log.info("Закрыто вопросов: %d", total)
    return total
