import json

from app.models import Question
from app.schemas.common import to_local


def _ai_answer(raw: str | None) -> dict | None:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"facts": [{"text": raw, "source": None}], "assessment": None}


def question_brief(question: Question) -> dict:
    return {
        "id": question.id,
        "text": question.text,
        "status": question.status,
        "created_at": to_local(question.created_at),
        "closed_at": to_local(question.closed_at),
        "author": question.user.public_name,
    }


def question_row(question: Question) -> dict:
    data = question_brief(question)
    data["news"] = {"id": question.news_id, "title": question.news.title}
    return data


def question_full(question: Question) -> dict:
    data = question_row(question)
    data["ai_answer"] = _ai_answer(question.ai_answer)
    data["official_answer"] = question.official_answer
    data["closing_news"] = (
        {
            "id": question.closing_news.id,
            "title": question.closing_news.title,
            "url": question.closing_news.url,
            "source": question.closing_news.source.name,
            "published_at": to_local(question.closing_news.published_at),
        }
        if question.closing_news
        else None
    )
    return data
