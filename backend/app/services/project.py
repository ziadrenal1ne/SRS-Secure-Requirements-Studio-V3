import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundError
from app.models.project import Project
from app.repositories.project import ProjectRepository
from app.schemas.project import ProjectUpdate


class ProjectService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.projects = ProjectRepository(session)

    async def list_projects(self) -> list[Project]:
        result = await self.session.execute(select(Project).order_by(Project.updated_at.desc()))
        return list(result.scalars().all())

    async def get_project(self, project_id: uuid.UUID) -> Project:
        project = await self.projects.get(project_id)
        if not project:
            raise NotFoundError("Project not found.")
        return project

    async def update_project(
        self, project_id: uuid.UUID, payload: ProjectUpdate
    ) -> Project:
        project = await self.get_project(project_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(project, field, value)
        await self.session.commit()
        await self.session.refresh(project)
        return project

    async def delete_project(self, project_id: uuid.UUID) -> None:
        project = await self.get_project(project_id)
        await self.projects.delete(project)
        await self.session.commit()
