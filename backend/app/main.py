from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import engine
from app.exceptions import DomainError
from app.logging import configure_logging, get_logger
from app.metrics import PrometheusMiddleware, metrics_endpoint
from app.models import Base  # noqa: F401 — ensures all models are registered
from app.routers import (
    ai_settings,
    documents,
    health,
    interview,
    knowledge_graph,
    public_projects,
    requirements,
    review,
    security,
)

settings = get_settings()
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup", environment=settings.environment)
    # Auto-create tables for SQLite (local dev without Docker/Alembic).
    # For PostgreSQL in production, rely on Alembic migrations instead.
    if settings.database_url.startswith("sqlite"):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("sqlite_tables_created")
    yield
    logger.info("shutdown")


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(PrometheusMiddleware)


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    logger.warning("domain_error", error_code=exc.error_code, message=exc.message, path=str(request.url))
    return JSONResponse(
        status_code=exc.status_code,
        content={"error_code": exc.error_code, "message": exc.message},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("unhandled_exception", error=str(exc), path=str(request.url))
    return JSONResponse(
        status_code=500,
        content={"error_code": "internal_error", "message": "An unexpected error occurred."},
    )


app.get("/metrics", include_in_schema=False)(metrics_endpoint)

app.include_router(health.router)
app.include_router(ai_settings.router, prefix=settings.api_v1_prefix)
app.include_router(public_projects.router, prefix=settings.api_v1_prefix)
app.include_router(knowledge_graph.router, prefix=settings.api_v1_prefix)
app.include_router(interview.router, prefix=settings.api_v1_prefix)
app.include_router(requirements.router, prefix=settings.api_v1_prefix)
app.include_router(security.router, prefix=settings.api_v1_prefix)
app.include_router(documents.router, prefix=settings.api_v1_prefix)
app.include_router(review.router, prefix=settings.api_v1_prefix)
