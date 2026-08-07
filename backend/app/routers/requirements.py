import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.requirement import RequirementOut, RequirementUpdate, TraceabilityMatrixRow
from app.services.project import ProjectService
from app.services.requirement import RequirementService

router = APIRouter(prefix="/projects/{project_id}/requirements", tags=["requirements"])


async def _authorize(project_id: uuid.UUID, db: AsyncSession) -> None:
    await ProjectService(db).get_project(project_id)


@router.get("", response_model=list[RequirementOut])
async def list_requirements(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[RequirementOut]:
    await _authorize(project_id, db)
    return await RequirementService(db).list_requirements(project_id)  # type: ignore[return-value]


@router.post("/generate", response_model=list[RequirementOut])
async def generate_missing_requirements(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[RequirementOut]:
    """Catch-up generation: creates requirements for any sufficiently
    completed Knowledge Graph node that doesn't have one yet. Safe to call
    repeatedly — generation is idempotent per concept."""
    await _authorize(project_id, db)
    return await RequirementService(db).generate_missing(project_id)  # type: ignore[return-value]


@router.get("/traceability-matrix", response_model=list[TraceabilityMatrixRow])
async def traceability_matrix(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[TraceabilityMatrixRow]:
    await _authorize(project_id, db)
    rows = await RequirementService(db).traceability_matrix(project_id)
    return [TraceabilityMatrixRow(**row) for row in rows]


@router.get("/{requirement_id}", response_model=RequirementOut)
async def get_requirement(
    project_id: uuid.UUID,
    requirement_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> RequirementOut:
    await _authorize(project_id, db)
    return await RequirementService(db).get_requirement(project_id, requirement_id)  # type: ignore[return-value]


@router.patch("/{requirement_id}", response_model=RequirementOut)
async def update_requirement(
    project_id: uuid.UUID,
    requirement_id: uuid.UUID,
    payload: RequirementUpdate,
    db: AsyncSession = Depends(get_db),
) -> RequirementOut:
    await _authorize(project_id, db)
    updates = payload.model_dump(exclude_unset=True)
    return await RequirementService(db).update_requirement(project_id, requirement_id, updates)  # type: ignore[return-value]
