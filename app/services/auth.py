import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import Conflict, Unauthorized, ValidationError
from app.core.security import hash_password, issue_token, read_token, verify_password
from app.models import User

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$")
MIN_PASSWORD = 8


def register(session: Session, *, email: str, password: str) -> tuple[User, str]:
    email = (email or "").strip().lower()
    if not _EMAIL.match(email):
        raise ValidationError("Некорректный email")
    if len(password or "") < MIN_PASSWORD:
        raise ValidationError(f"Пароль короче {MIN_PASSWORD} символов")
    if session.scalar(select(User).where(User.email == email)) is not None:
        raise Conflict("Пользователь с таким email уже зарегистрирован")

    user = User(email=email, password_hash=hash_password(password))
    session.add(user)
    session.flush()
    return user, issue_token(user.id)


def login(session: Session, *, email: str, password: str) -> tuple[User, str]:
    user = session.scalar(select(User).where(User.email == (email or "").strip().lower()))
    if user is None or not verify_password(password or "", user.password_hash):
        raise Unauthorized("Неверный email или пароль")
    if not user.is_active:
        raise Unauthorized("Учётная запись отключена")
    return user, issue_token(user.id)


def user_from_token(session: Session, token: str) -> User:
    user = session.get(User, read_token(token))
    if user is None or not user.is_active:
        raise Unauthorized("Сессия недействительна")
    return user
