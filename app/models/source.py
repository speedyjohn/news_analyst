from datetime import datetime

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models.base import ts_column


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    country: Mapped[str] = mapped_column(String(10), default="KZ")
    category_hint: Mapped[str | None] = mapped_column(String(30))
    type: Mapped[str] = mapped_column(String(10), default="rss")  # rss | html
    url: Mapped[str] = mapped_column(String(500))
    feed_url: Mapped[str | None] = mapped_column(String(500))
    parser: Mapped[str] = mapped_column(String(50), default="rss")
    priority: Mapped[int] = mapped_column(Integer, default=3)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    last_success_at: Mapped[datetime | None] = ts_column()
