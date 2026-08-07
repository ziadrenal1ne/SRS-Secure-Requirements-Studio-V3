import uuid

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.interview import InterviewSession, InterviewTurn
from app.repositories.base import BaseRepository


class InterviewSessionRepository(BaseRepository[InterviewSession]):
    model = InterviewSession

    async def get_active_for_project(self, project_id: uuid.UUID) -> InterviewSession | None:
        result = await self.session.execute(
            select(InterviewSession)
            .where(
                InterviewSession.project_id == project_id,
                InterviewSession.status.in_(("active", "paused")),
            )
            .options(selectinload(InterviewSession.turns))
            .order_by(InterviewSession.created_at.desc())
        )
        return result.scalars().first()

    async def get_with_turns(self, session_id: uuid.UUID) -> InterviewSession | None:
        result = await self.session.execute(
            select(InterviewSession)
            .where(InterviewSession.id == session_id)
            .options(selectinload(InterviewSession.turns))
        )
        return result.scalar_one_or_none()


class InterviewTurnRepository(BaseRepository[InterviewTurn]):
    model = InterviewTurn
