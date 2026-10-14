from datetime import datetime

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models.base import ts_column, utcnow


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    started_at: Mapped[datetime] = ts_column(default=utcnow, index=True)
    finished_at: Mapped[datetime | None] = ts_column()
    source_code: Mapped[str] = mapped_column(String(50), index=True)
    status: Mapped[str] = mapped_column(String(10), default="ok")  # ok | failed
    items_found: Mapped[int] = mapped_column(Integer, default=0)
    items_saved: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str | None] = mapped_column(Text)
