from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import mapped_column


def utcnow() -> datetime:
    return datetime.now(UTC)


def ts_column(**kw):
    return mapped_column(DateTime(timezone=True), **kw)
