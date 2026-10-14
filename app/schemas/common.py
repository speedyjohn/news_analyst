from datetime import datetime
from zoneinfo import ZoneInfo

from app.core.config import settings

LOCAL_TZ = ZoneInfo(settings.timezone)


def to_local(value: datetime | None) -> str | None:
    return value.astimezone(LOCAL_TZ).isoformat() if value else None
