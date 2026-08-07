import uuid

from sqlalchemy import select

from app.models.generated_document import GeneratedDocument
from app.repositories.base import BaseRepository


class GeneratedDocumentRepository(BaseRepository[GeneratedDocument]):
    model = GeneratedDocument

    async def get_for_project(self, project_id: uuid.UUID) -> GeneratedDocument | None:
        result = await self.session.execute(
            select(GeneratedDocument).where(GeneratedDocument.project_id == project_id)
        )
        return result.scalar_one_or_none()
