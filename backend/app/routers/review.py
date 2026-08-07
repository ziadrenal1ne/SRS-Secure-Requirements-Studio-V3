import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.review import ReviewRunOut
from app.services.project import ProjectService
from app.services.review_engine import ReviewEngineService

router = APIRouter(prefix="/projects/{project_id}/review", tags=["review"])


async def _authorize(project_id: uuid.UUID, db: AsyncSession) -> None:
    await ProjectService(db).get_project(project_id)


@router.post("/run", response_model=ReviewRunOut)
async def run_review(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ReviewRunOut:
    """Runs the full validation rule set (completeness, security,
    architecture, business, testing) and returns per-rule findings plus
    the six 0-100 scores. Safe to call repeatedly — overwrites the
    previous run rather than duplicating it."""
    await _authorize(project_id, db)
    return await ReviewEngineService(db).run_review(project_id)  # type: ignore[return-value]


@router.get("", response_model=ReviewRunOut)
async def get_review(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ReviewRunOut:
    await _authorize(project_id, db)
    return await ReviewEngineService(db).get_review(project_id)  # type: ignore[return-value]
