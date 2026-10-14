from openai import OpenAI

from app.llm.base import TimedProvider


class OpenAIProvider(TimedProvider):
    name = "openai"

    def __init__(self, model: str, api_key: str, timeout: int = 60, **kw):
        super().__init__(model, api_key, timeout)
        self._client = OpenAI(api_key=api_key, timeout=float(timeout), base_url=kw.get("base_url") or None)

    def _raw_complete(self, system: str, user: str, max_tokens: int) -> str:
        response = self._client.chat.completions.create(
            model=self.model,
            max_completion_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        usage = response.usage
        if usage:
            self.last_usage = (usage.prompt_tokens, usage.completion_tokens)
        return response.choices[0].message.content or ""
