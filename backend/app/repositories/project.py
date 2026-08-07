import uuid

from sqlalchemy import select

from app.models.project import Project
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    model = Project

    async def list_for_organization(
        self, organization_id: uuid.UUID, *, limit: int = 100, offset: int = 0
    ) -> list[Project]:
        result = await self.session.execute(
            select(Project)
            .where(Project.organization_id == organization_id)
            .order_by(Project.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
