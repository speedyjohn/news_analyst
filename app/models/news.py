from datetime import datetime

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.base import ts_column, utcnow
from app.models.source import Source


class News(Base):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), index=True)
    title: Mapped[str] = mapped_column(String(700))
    full_text: Mapped[str] = mapped_column(Text, default="")
    summary: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str] = mapped_column(String(1000), unique=True)
    published_at: Mapped[datetime] = ts_column(index=True)
    parsed_at: Mapped[datetime] = ts_column(default=utcnow)
    language: Mapped[str] = mapped_column(String(5), default="ru")
    country: Mapped[str] = mapped_column(String(10), default="KZ")
    category: Mapped[str | None] = mapped_column(String(30))
    importance_score: Mapped[int | None] = mapped_column(Integer, index=True)
    importance_reason: Mapped[str | None] = mapped_column(Text)
    content_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)

    source: Mapped[Source] = relationship(lazy="joined")


Index("ix_news_published_score", News.published_at.desc(), News.importance_score.desc())
