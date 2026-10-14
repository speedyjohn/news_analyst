import json
import logging
import re
import time
from abc import ABC, abstractmethod
from typing import Any

from app.core.errors import LLMError

log = logging.getLogger(__name__)

_FENCE = re.compile(r"^\s*```(?:json)?\s*|\s*```\s*$", re.IGNORECASE)


def strip_json_fence(raw: str) -> str:
    text = _FENCE.sub("", raw.strip())
    # бывает, что перед JSON модель пишет пояснение
    start = min((i for i in (text.find("{"), text.find("[")) if i != -1), default=-1)
    if start == -1:
        return text
    end = max(text.rfind("}"), text.rfind("]"))
    return text[start : end + 1] if end > start else text[start:]


class LLMProvider(ABC):
    name = "base"

    def __init__(self, model: str, api_key: str, timeout: int = 60):
        self.model = model
        self.api_key = api_key
        self.timeout = timeout
        self.last_usage: tuple[int, int] = (0, 0)

    @abstractmethod
    def complete(self, system: str, user: str, max_tokens: int = 1500) -> str: ...

    def complete_json(
        self, system: str, user: str, schema: dict[str, Any] | None = None, max_tokens: int = 1500
    ) -> Any:
        hint = "\n\nОтветь строго валидным JSON без пояснений и без markdown-обёртки."
        if schema:
            hint += f" Схема ответа: {json.dumps(schema, ensure_ascii=False)}"

        last_raw = ""
        for attempt in (1, 2):
            raw = self.complete(system + hint, user, max_tokens=max_tokens)
            last_raw = raw
            try:
                return json.loads(strip_json_fence(raw))
            except json.JSONDecodeError:
                log.warning("Ответ модели не разобран как JSON (попытка %d): %.300s", attempt, raw)
                user = (
                    f"{user}\n\nПредыдущий ответ не был валидным JSON. "
                    "Верни только JSON-объект, без единого символа вне него."
                )
        raise LLMError(f"Модель не вернула валидный JSON: {last_raw[:200]}")


class TimedProvider(LLMProvider):
    @abstractmethod
    def _raw_complete(self, system: str, user: str, max_tokens: int) -> str: ...

    def complete(self, system: str, user: str, max_tokens: int = 1500) -> str:
        started = time.monotonic()
        try:
            result = self._raw_complete(system, user, max_tokens)
        except Exception as exc:  # noqa: BLE001
            log.exception("LLM %s/%s упал", self.name, self.model)
            raise LLMError(f"Модель недоступна: {exc}") from exc
        duration = int((time.monotonic() - started) * 1000)
        log.info(
            "LLM %s/%s ok за %d мс, токены %s",
            self.name,
            self.model,
            duration,
            self.last_usage,
        )
        self.last_duration_ms = duration
        return result
