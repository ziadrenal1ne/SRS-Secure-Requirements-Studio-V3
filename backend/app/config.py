"""Centralized application configuration.

All runtime configuration is sourced from environment variables (or a
.env file in local development) via pydantic-settings. Nothing here is
hardcoded so the same image can run in dev/staging/prod by swapping env
vars only.
"""
from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- App ---
    app_name: str = "Secure Requirements Studio API"
    environment: Literal["development", "test", "staging", "production"] = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # --- Database ---
    database_url: str = Field(
        default="postgresql+asyncpg://srs:srs@localhost:5432/srs",
        description="Async SQLAlchemy DSN. Use sqlite+aiosqlite:///... for tests.",
    )

    # --- Redis / Celery ---
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # --- Auth ---
    # Auth is removed, so JWT keys are not needed.

    # --- CORS ---
    cors_allow_origins: list[str] = ["http://localhost:3000"]

    # --- Object storage (exports/documents) ---
    storage_endpoint: str = "http://localhost:9000"
    storage_bucket: str = "srs-documents"
    storage_access_key: str = "minioadmin"
    storage_secret_key: str = "minioadmin"

    # --- AI (Interview Engine) ---
    ai_provider: Literal["gemini", "template"] = "template"
    gemini_api_key: str | None = Field(default=None, description="Google Gemini API key.")
    gemini_model: str = "gemini-3.5-flash-lite"
    gemini_timeout_seconds: float = 60.0
    gemini_temperature: float = 0.2
    gemini_top_p: float = 0.95
    gemini_max_output_tokens: int = 2048
    gemini_enable_streaming: bool = False

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
