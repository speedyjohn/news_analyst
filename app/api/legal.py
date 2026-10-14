from flask import Blueprint, g, jsonify, request

from app.api.deps import auth_required, get_llm, open_session
from app.schemas.legal import legal_request
from app.services import legal as legal_service

bp = Blueprint("legal", __name__, url_prefix="/api/legal")


@bp.post("/suggest")
@auth_required
def suggest():
    session = open_session()
    legal_service.require_corpus(session)
    result = legal_service.suggest(
        session,
        get_llm(),
        user=g.user,
        text=(request.get_json(silent=True) or {}).get("text", ""),
    )
    session.commit()
    return jsonify(legal_request(result)), 201


@bp.get("/requests/mine")
@auth_required
def mine():
    session = open_session()
    rows = legal_service.requests_of(session, g.user)
    return jsonify({"items": [legal_request(r) for r in rows]})
