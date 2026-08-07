from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from app.config import Settings, get_settings


class AIProviderSettings(BaseModel):
    provider: Literal["template", "gemini"] = "template"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.5-flash-lite"
    gemini_temperature: float = 0.2
    gemini_top_p: float = 0.95
    gemini_max_output_tokens: int = 2048
    gemini_timeout_seconds: float = 60.0
    gemini_enable_streaming: bool = False


class EffectiveAISettings(AIProviderSettings):
    gemini_api_key: str | None = None


_CONFIG_PATH = Path(__file__).resolve().parents[2] / ".ai-provider.local.json"


def _from_environment(settings: Settings) -> EffectiveAISettings:
    provider = settings.ai_provider
    return EffectiveAISettings(
        provider="gemini" if provider == "gemini" else "template",
        gemini_api_key=settings.gemini_api_key,
        gemini_model=settings.gemini_model,
        gemini_temperature=settings.gemini_temperature,
        gemini_top_p=settings.gemini_top_p,
        gemini_max_output_tokens=settings.gemini_max_output_tokens,
        gemini_timeout_seconds=settings.gemini_timeout_seconds,
        gemini_enable_streaming=settings.gemini_enable_streaming,
    )


def load_ai_settings() -> EffectiveAISettings:
    current = _from_environment(get_settings())
    if not _CONFIG_PATH.exists():
        return current
    try:
        saved = AIProviderSettings.model_validate_json(_CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return current
    data = saved.model_dump()
    if not saved.gemini_api_key:
        data["gemini_api_key"] = current.gemini_api_key
    return current.model_copy(update=data)


def save_ai_settings(settings: AIProviderSettings) -> EffectiveAISettings:
    current = _from_environment(get_settings())
    api_key = settings.gemini_api_key or current.gemini_api_key
    stored = settings.model_copy(update={"gemini_api_key": api_key})
    _CONFIG_PATH.write_text(stored.model_dump_json(indent=2), encoding="utf-8")
    return load_ai_settings()


def public_ai_settings(settings: EffectiveAISettings | None = None) -> dict:
    effective = settings or load_ai_settings()
    data = effective.model_dump(exclude={"gemini_api_key"})
    data["gemini_api_key_configured"] = bool(effective.gemini_api_key)
    return data
