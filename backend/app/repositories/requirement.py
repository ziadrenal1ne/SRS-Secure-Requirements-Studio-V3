import uuid

from sqlalchemy import func, select

from app.models.requirement import Requirement
from app.repositories.base import BaseRepository


class RequirementRepository(BaseRepository[Requirement]):
    model = Requirement

    async def list_for_project(self, project_id: uuid.UUID) -> list[Requirement]:
        result = await self.session.execute(
            select(Requirement)
            .where(Requirement.project_id == project_id)
            .order_by(Requirement.requirement_key)
        )
        return list(result.scalars().all())

    async def get_by_source_concept(
        self, project_id: uuid.UUID, concept_key: str
    ) -> Requirement | None:
        result = await self.session.execute(
            select(Requirement).where(
                Requirement.project_id == project_id,
                Requirement.source_concept_key == concept_key,
            )
        )
        return result.scalar_one_or_none()

    async def count_for_type(self, project_id: uuid.UUID, requirement_type: str) -> int:
        result = await self.session.execute(
            select(func.count()).where(
                Requirement.project_id == project_id,
                Requirement.requirement_type == requirement_type,
            )
        )
        return result.scalar_one()
