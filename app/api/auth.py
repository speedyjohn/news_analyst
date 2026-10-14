from flask import Blueprint, g, jsonify, make_response, request

from app.api.deps import auth_required, open_session
from app.core.config import settings
from app.schemas.auth import user_public
from app.services import auth as auth_service

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _with_cookie(payload: dict, token: str, status: int = 200):
    response = make_response(jsonify(payload), status)
    response.set_cookie(
        settings.cookie_name,
        token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="Lax",
        max_age=settings.jwt_ttl_hours * 3600,
        path="/",
    )
    return response


@bp.post("/register")
def register():
    session = open_session()
    body = request.get_json(silent=True) or {}
    user, token = auth_service.register(session, email=body.get("email", ""), password=body.get("password", ""))
    session.commit()
    return _with_cookie(user_public(user), token, 201)


@bp.post("/login")
def login():
    session = open_session()
    body = request.get_json(silent=True) or {}
    user, token = auth_service.login(session, email=body.get("email", ""), password=body.get("password", ""))
    return _with_cookie(user_public(user), token)


@bp.post("/logout")
def logout():
    response = make_response(jsonify({"ok": True}))
    response.delete_cookie(settings.cookie_name, path="/")
    return response


@bp.get("/me")
@auth_required
def me():
    return jsonify(user_public(g.user))
