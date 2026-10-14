from app.core.config import Settings, settings
from app.core.errors import AppError
from app.llm.base import LLMProvider
from app.llm.claude import ClaudeProvider
from app.llm.deepseek import DeepSeekProvider
from app.llm.openai import OpenAIProvider

_PROVIDERS: dict[str, type[LLMProvider]] = {
    "claude": ClaudeProvider,
    "openai": OpenAIProvider,
    "deepseek": DeepSeekProvider,
}


def build_llm(cfg: Settings | None = None) -> LLMProvider:
    cfg = cfg or settings
    provider_cls = _PROVIDERS.get(cfg.llm_provider.lower())
    if provider_cls is None:
        raise AppError(
            f"Неизвестный LLM_PROVIDER={cfg.llm_provider}. Доступны: {', '.join(_PROVIDERS)}",
            code="config_error",
            status=500,
        )
    if not cfg.llm_api_key:
        raise AppError("LLM_API_KEY не задан", code="config_error", status=500)
    return provider_cls(
        model=cfg.llm_model,
        api_key=cfg.llm_api_key,
        timeout=cfg.llm_timeout,
        base_url=cfg.llm_base_url,
        effort=cfg.llm_effort,
        refusal_fallback=cfg.llm_refusal_fallback,
    )
