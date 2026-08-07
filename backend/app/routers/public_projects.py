import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.exceptions import NotFoundError
from app.models.organization import Organization
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectOut, ProjectUpdate
from app.services.knowledge_graph import KnowledgeGraphService

router = APIRouter(prefix="/projects", tags=["projects"])

FOCP_ORG_SLUG = "fondation-ocp-internal"
FOCP_OWNER_EMAIL = "studio@fondation-ocp.internal"


async def _internal_context(db: AsyncSession) -> tuple[Organization, User]:
    org = await db.scalar(select(Organization).where(Organization.slug == FOCP_ORG_SLUG))
    if org is None:
        org = Organization(name="Fondation OCP", slug=FOCP_ORG_SLUG)
        db.add(org)
        await db.flush()

    owner = await db.scalar(select(User).where(User.email == FOCP_OWNER_EMAIL))
    if owner is None:
        owner = User(
            email=FOCP_OWNER_EMAIL,
            hashed_password="internal-no-auth",
            full_name="FOCP Secure Requirements Studio",
            is_active=True,
            is_superuser=True,
        )
        db.add(owner)
        await db.flush()

    return org, owner


@router.get("", response_model=list[ProjectOut])
async def list_projects(db: AsyncSession = Depends(get_db)) -> list[Project]:
    result = await db.execute(select(Project).order_by(Project.updated_at.desc()))
    return list(result.scalars().all())


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project(payload: ProjectCreate, db: AsyncSession = Depends(get_db)) -> Project:
    org, owner = await _internal_context(db)
    project = Project(
        **payload.model_dump(),
        organization_id=org.id,
        owner_id=owner.id,
        status="en_cours",
        progress=5,
        security_score=70,
    )
    db.add(project)
    await db.flush()
    await KnowledgeGraphService(db).seed_project_graph(project.id)
    await db.commit()
    await db.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(project_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> Project:
    project = await db.get(Project, project_id)
    if project is None:
        raise NotFoundError("Project not found.")
    return project


@router.patch("/{project_id}", response_model=ProjectOut)
async def update_project(
    project_id: uuid.UUID,
    payload: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
) -> Project:
    project = await get_project(project_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    await db.commit()
    await db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> None:
    project = await get_project(project_id, db)
    await db.delete(project)
    await db.commit()
