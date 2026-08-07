import asyncio

from fastapi import APIRouter

from app.services.ai_settings import AIProviderSettings, load_ai_settings, public_ai_settings, save_ai_settings
from app.services.llm_client import reset_llm_client_cache

router = APIRouter(prefix="/ai", tags=["ai-settings"])


def _load_google_genai():
    try:
        from google import genai
        from google.genai import types

        return genai, types
    except Exception as exc:
        raise RuntimeError(
            "Google GenAI SDK is not installed in the backend runtime. "
            "Install it where FastAPI runs with: pip install google-genai"
        ) from exc


async def test_gemini_connection(settings: AIProviderSettings) -> dict:
    api_key = settings.gemini_api_key or load_ai_settings().gemini_api_key
    if not api_key:
        return {
            "status": "error",
            "connected": False,
            "model_available": False,
            "provider": "gemini",
            "model": settings.gemini_model,
            "error": "Gemini API key is not configured.",
        }

    def request() -> str:
        genai, types = _load_google_genai()
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents="Reply with the single word: ok",
            config=types.GenerateContentConfig(temperature=0, max_output_tokens=8),
        )
        return response.text or ""

    try:
        text = await asyncio.wait_for(
            asyncio.to_thread(request),
            timeout=min(settings.gemini_timeout_seconds, 20),
        )
        connected = bool(text.strip())
        return {
            "status": "ok" if connected else "error",
            "connected": connected,
            "model_available": connected,
            "provider": "gemini",
            "model": settings.gemini_model,
            "error": None if connected else "Gemini returned an empty response.",
        }
    except Exception as exc:
        return {
            "status": "error",
            "connected": False,
            "model_available": False,
            "provider": "gemini",
            "model": settings.gemini_model,
            "error": str(exc),
        }


@router.get("/settings")
async def get_ai_settings() -> dict:
    return public_ai_settings()


@router.put("/settings")
async def update_ai_settings(settings: AIProviderSettings) -> dict:
    effective = save_ai_settings(settings)
    reset_llm_client_cache()
    return public_ai_settings(effective)


@router.post("/test")
async def test_ai_settings(settings: AIProviderSettings) -> dict:
    if settings.provider == "template":
        return {
            "status": "fallback",
            "connected": True,
            "model_available": True,
            "provider": "template",
            "model": "template-assistant",
            "error": None,
        }
    return await test_gemini_connection(settings)
