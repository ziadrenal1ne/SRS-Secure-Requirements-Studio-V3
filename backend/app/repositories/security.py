import uuid

from sqlalchemy import select

from app.models.security import SecurityAnalysis
from app.repositories.base import BaseRepository


class SecurityAnalysisRepository(BaseRepository[SecurityAnalysis]):
    model = SecurityAnalysis

    async def get_for_project(self, project_id: uuid.UUID) -> SecurityAnalysis | None:
        result = await self.session.execute(
            select(SecurityAnalysis).where(SecurityAnalysis.project_id == project_id)
        )
        return result.scalar_one_or_none()
