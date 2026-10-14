from collections.abc import Callable
from functools import wraps

from flask import g, request

from app.core.config import settings
from app.core.db import SessionLocal
from app.core.errors import Unauthorized
from app.llm.factory import build_llm
from app.services import auth as auth_service

_llm = None


def get_llm():
    global _llm
    if _llm is None:
        _llm = build_llm()
    return _llm


def open_session():
    if "db" not in g:
        g.db = SessionLocal()
    return g.db


def close_session(exception=None) -> None:
    session = g.pop("db", None)
    if session is None:
        return
    if exception is None:
        session.commit()
    else:
        session.rollback()
    session.close()


def _token() -> str | None:
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        return header[7:]
    return request.cookies.get(settings.cookie_name)


def current_user(required: bool = True):
    token = _token()
    if not token:
        if required:
            raise Unauthorized("Требуется вход")
        return None
    return auth_service.user_from_token(open_session(), token)


def auth_required(view: Callable) -> Callable:
    @wraps(view)
    def wrapper(*args, **kwargs):
        g.user = current_user(required=True)
        return view(*args, **kwargs)

    return wrapper
