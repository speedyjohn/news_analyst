from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import NotFound
from app.models import STATUS_CLOSED, STATUS_OPEN, Question, User


def for_news(session: Session, news_id: int) -> list[Question]:
    return list(
        session.scalars(
            select(Question).where(Question.news_id == news_id).order_by(Question.created_at.desc())
        )
    )


def get(session: Session, question_id: int) -> Question:
    question = session.get(Question, question_id)
    if question is None:
        raise NotFound("Вопрос не найден")
    return question


def mine(session: Session, user: User, *, status: str | None = None) -> dict:
    query = select(Question).where(Question.user_id == user.id)
    if status in (STATUS_OPEN, STATUS_CLOSED):
        query = query.where(Question.status == status)
    items = list(session.scalars(query.order_by(Question.created_at.desc())))

    all_mine = session.scalars(
        select(Question.status).where(Question.user_id == user.id)
    ).all()
    return {
        "items": items,
        "open": sum(1 for s in all_mine if s == STATUS_OPEN),
        "closed": sum(1 for s in all_mine if s == STATUS_CLOSED),
    }
