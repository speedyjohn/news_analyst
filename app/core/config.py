from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+psycopg://news:news@localhost:5432/news"
    secret_key: str = "dev-secret-change-me"
    timezone: str = "Asia/Almaty"
    public_base_url: str = "http://localhost:5173"

    llm_provider: str = "claude"
    llm_model: str = "claude-opus-5"
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_timeout: int = 60
    llm_effort: str = "medium"  # low | medium | high | xhigh | max
    llm_refusal_fallback: bool = True
    llm_daily_call_limit: int = 2000

    ingestion_hour: int = 7
    ingestion_minute: int = 0
    http_timeout: int = 20
    http_verify_ssl: bool = True
    ingestion_max_items: int = 40

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "noreply@localhost"
    smtp_tls: bool = True

    questions_per_day: int = 15
    questions_per_hour: int = 5
    legal_per_day: int = 5

    jwt_ttl_hours: int = 720
    cookie_name: str = "auth"
    cookie_secure: bool = False

    @field_validator("database_url")
    @classmethod
    def _force_psycopg_driver(cls, value: str) -> str:
        # хостинги отдают postgres://, а у нас psycopg 3
        for scheme in ("postgres://", "postgresql://"):
            if value.startswith(scheme):
                return "postgresql+psycopg://" + value[len(scheme) :]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
