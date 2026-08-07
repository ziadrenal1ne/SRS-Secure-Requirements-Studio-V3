from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.routers.ai_settings import test_gemini_connection
from app.services.ai_settings import AIProviderSettings, load_ai_settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def liveness() -> dict:
    """Liveness probe — process is up. Never touches the DB."""
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness(db: AsyncSession = Depends(get_db)) -> dict:
    """Readiness probe — dependencies (DB) are reachable."""
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    status = "ok" if db_ok else "degraded"
    return {"status": status, "checks": {"database": db_ok}}


@router.get("/health/ai")
@router.get("/api/v1/health/ai")
async def ai_health() -> dict:
    """Check AI engine connectivity and model availability."""
    ai_settings = load_ai_settings()
    if ai_settings.provider == "gemini":
        return await test_gemini_connection(AIProviderSettings(**ai_settings.model_dump()))
    return {
        "status": "fallback",
        "connected": True,
        "model_available": True,
        "provider": "template",
        "model": "template-heuristic",
        "error": None,
    }

