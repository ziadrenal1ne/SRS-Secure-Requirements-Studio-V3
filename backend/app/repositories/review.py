import uuid

from sqlalchemy import select

from app.models.review import ReviewRun
from app.repositories.base import BaseRepository


class ReviewRunRepository(BaseRepository[ReviewRun]):
    model = ReviewRun

    async def get_for_project(self, project_id: uuid.UUID) -> ReviewRun | None:
        result = await self.session.execute(
            select(ReviewRun).where(ReviewRun.project_id == project_id)
        )
        return result.scalar_one_or_none()
