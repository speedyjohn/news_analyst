from datetime import datetime

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.base import ts_column, utcnow
from app.models.news import News
from app.models.user import User

STATUS_OPEN = "open"
STATUS_CLOSED = "closed"


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    news_id: Mapped[int] = mapped_column(ForeignKey("news.id"), index=True)
    text: Mapped[str] = mapped_column(Text)
    ai_answer: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(10), default=STATUS_OPEN, index=True)
    official_answer: Mapped[str | None] = mapped_column(Text)
    closing_news_id: Mapped[int | None] = mapped_column(ForeignKey("news.id"))
    created_at: Mapped[datetime] = ts_column(default=utcnow, index=True)
    closed_at: Mapped[datetime | None] = ts_column()

    user: Mapped[User] = relationship(back_populates="questions", foreign_keys=[user_id], lazy="joined")
    news: Mapped[News] = relationship(foreign_keys=[news_id], lazy="joined")
    closing_news: Mapped[News | None] = relationship(foreign_keys=[closing_news_id], lazy="joined")
