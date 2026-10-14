from app.llm.openai import OpenAIProvider

DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"


class DeepSeekProvider(OpenAIProvider):
    name = "deepseek"

    def __init__(self, model: str, api_key: str, timeout: int = 60, **kw):
        # не setdefault: при пустом LLM_BASE_URL приходит ""
        if not kw.get("base_url"):
            kw["base_url"] = DEEPSEEK_BASE_URL
        super().__init__(model, api_key, timeout, **kw)
