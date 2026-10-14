import anthropic

from app.core.errors import LLMError
from app.llm.base import TimedProvider


class ClaudeProvider(TimedProvider):
    name = "claude"

    def __init__(self, model: str, api_key: str, timeout: int = 60, **kw):
        super().__init__(model, api_key, timeout)
        self.effort = kw.get("effort", "medium")
        self.refusal_fallback = kw.get("refusal_fallback", True)
        self._client = anthropic.Anthropic(api_key=api_key, timeout=float(timeout))

    def _raw_complete(self, system: str, user: str, max_tokens: int) -> str:
        params = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": user}],
            "output_config": {"effort": self.effort},
        }

        if self.refusal_fallback:
            response = self._client.beta.messages.create(
                betas=["server-side-fallback-2026-07-01"], fallbacks="default", **params
            )
        else:
            response = self._client.messages.create(**params)

        if response.stop_reason == "refusal":
            detail = getattr(response.stop_details, "explanation", None) or "без пояснения"
            raise LLMError(f"Модель отклонила запрос: {detail}")

        self.last_usage = (response.usage.input_tokens, response.usage.output_tokens)
        return "".join(block.text for block in response.content if block.type == "text")
