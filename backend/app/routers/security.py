import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.security import SecurityAnalysisOut
from app.services.project import ProjectService
from app.services.security_engine import SecurityEngineService

router = APIRouter(prefix="/projects/{project_id}/security", tags=["security"])


async def _authorize(project_id: uuid.UUID, db: AsyncSession) -> None:
    await ProjectService(db).get_project(project_id)


@router.post("/analyze", response_model=SecurityAnalysisOut)
async def analyze(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> SecurityAnalysisOut:
    """Runs (or re-runs) the full Security Engine analysis for this
    project: threat model, RBAC matrix, risk register, checklist, PIA,
    and data classification, all derived from current Knowledge Graph
    and Requirements state. Safe to call repeatedly — overwrites the
    previous analysis rather than duplicating it."""
    await _authorize(project_id, db)
    return await SecurityEngineService(db).analyze(project_id)  # type: ignore[return-value]


@router.get("", response_model=SecurityAnalysisOut)
async def get_analysis(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> SecurityAnalysisOut:
    await _authorize(project_id, db)
    return await SecurityEngineService(db).get_analysis(project_id)  # type: ignore[return-value]
