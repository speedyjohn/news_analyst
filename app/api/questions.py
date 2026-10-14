from flask import Blueprint, g, jsonify, request

from app.api.deps import auth_required, get_llm, open_session
from app.schemas.questions import question_brief, question_full, question_row
from app.services import qa as qa_service
from app.services import questions as questions_service

bp = Blueprint("questions", __name__, url_prefix="/api")


@bp.get("/news/<int:news_id>/questions")
def by_news(news_id: int):
    session = open_session()
    return jsonify(
        {"items": [question_brief(q) for q in questions_service.for_news(session, news_id)]}
    )


@bp.post("/news/<int:news_id>/questions")
@auth_required
def ask(news_id: int):
    session = open_session()
    question = qa_service.ask(
        session,
        get_llm(),
        user=g.user,
        news_id=news_id,
        text=(request.get_json(silent=True) or {}).get("text", ""),
    )
    session.commit()
    return jsonify(question_full(question)), 201


@bp.get("/questions/mine")
@auth_required
def mine():
    session = open_session()
    payload = questions_service.mine(session, g.user, status=request.args.get("status"))
    return jsonify(
        {
            "items": [question_row(q) for q in payload["items"]],
            "open": payload["open"],
            "closed": payload["closed"],
        }
    )


@bp.get("/questions/<int:question_id>")
def one(question_id: int):
    session = open_session()
    return jsonify(question_full(questions_service.get(session, question_id)))
