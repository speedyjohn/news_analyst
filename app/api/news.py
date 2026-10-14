from datetime import date

from flask import Blueprint, jsonify, request

from app.api.deps import open_session
from app.core.errors import ValidationError
from app.schemas.news import feed_response, news_full
from app.schemas.questions import question_brief
from app.services import news as news_service
from app.services import questions as questions_service

bp = Blueprint("news", __name__, url_prefix="/api/news")


def _date_arg(raw: str | None) -> date | None:
    if not raw:
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError as exc:
        raise ValidationError("Дата должна быть в формате YYYY-MM-DD") from exc


def _int_arg(raw: str | None) -> int | None:
    try:
        return int(raw) if raw else None
    except ValueError as exc:
        raise ValidationError("Ожидалось число") from exc


@bp.get("")
def feed():
    session = open_session()
    payload = news_service.feed(
        session,
        day=_date_arg(request.args.get("date")),
        top=_int_arg(request.args.get("top")),
        category=request.args.get("category"),
        region=request.args.get("region"),
        page=_int_arg(request.args.get("page")) or 1,
    )
    return jsonify(feed_response(payload))


@bp.get("/dates")
def dates():
    session = open_session()
    return jsonify({"dates": [d.isoformat() for d in news_service.available_dates(session)]})


@bp.get("/<int:news_id>")
def one(news_id: int):
    session = open_session()
    news = news_service.get_news(session, news_id)
    return jsonify(
        {
            **news_full(news),
            "questions_list": [question_brief(q) for q in questions_service.for_news(session, news_id)],
        }
    )
