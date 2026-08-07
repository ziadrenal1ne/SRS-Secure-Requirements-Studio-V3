import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.knowledge_graph import (
    KnowledgeGraphNodeOut,
    KnowledgeGraphOut,
    ProjectCompletionOut,
)
from app.services.knowledge_graph import KnowledgeGraphService
from app.services.project import ProjectService

router = APIRouter(prefix="/projects/{project_id}/knowledge-graph", tags=["knowledge-graph"])


async def _authorize(project_id: uuid.UUID, db: AsyncSession) -> None:
    """Every KG endpoint is scoped through project access, since a
    project's graph is only visible to members of its organization."""
    await ProjectService(db).get_project(project_id)


@router.get("", response_model=KnowledgeGraphOut)
async def get_graph(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> KnowledgeGraphOut:
    await _authorize(project_id, db)
    nodes, edges = await KnowledgeGraphService(db).get_graph(project_id)
    return KnowledgeGraphOut(nodes=nodes, edges=edges)  # type: ignore[arg-type]


@router.get("/gaps", response_model=list[KnowledgeGraphNodeOut])
async def get_gaps(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[KnowledgeGraphNodeOut]:
    await _authorize(project_id, db)
    return await KnowledgeGraphService(db).compute_gaps(project_id)  # type: ignore[return-value]


@router.get("/next-concept", response_model=KnowledgeGraphNodeOut | None)
async def get_next_concept(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> KnowledgeGraphNodeOut | None:
    await _authorize(project_id, db)
    return await KnowledgeGraphService(db).next_concept(project_id)  # type: ignore[return-value]


@router.get("/completion", response_model=ProjectCompletionOut)
async def get_completion(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ProjectCompletionOut:
    await _authorize(project_id, db)
    data = await KnowledgeGraphService(db).project_completion(project_id)
    return ProjectCompletionOut(**data)
