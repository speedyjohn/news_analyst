import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import LLMError
from app.llm.base import LLMProvider
from app.models import LLMCall

log = logging.getLogger(__name__)


def calls_today(session: Session) -> int:
    since = datetime.now(UTC) - timedelta(days=1)
    return session.scalar(select(func.count(LLMCall.id)).where(LLMCall.created_at >= since)) or 0


def ask_json(
    session: Session,
    llm: LLMProvider,
    *,
    task: str,
    system: str,
    user: str,
    schema: dict[str, Any] | None = None,
    max_tokens: int = 1500,
    user_facing: bool = True,
) -> Any:
    if user_facing and calls_today(session) >= settings.llm_daily_call_limit:
        raise LLMError("Суточный лимит обращений к модели исчерпан, попробуйте завтра")

    record = LLMCall(task=task, provider=llm.name, model=llm.model)
    try:
        result = llm.complete_json(system, user, schema, max_tokens=max_tokens)
    except Exception as exc:
        record.ok = False
        record.error = str(exc)[:2000]
        session.add(record)
        session.flush()
        raise
    record.tokens_in, record.tokens_out = llm.last_usage
    record.duration_ms = getattr(llm, "last_duration_ms", 0)
    session.add(record)
    session.flush()
    log.info("LLM задача %s выполнена", task)
    return result
