import uuid
from typing import Literal

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.document import GeneratedDocumentOut
from app.services.document_generator import DocumentGeneratorService
from app.services.project import ProjectService

router = APIRouter(prefix="/projects/{project_id}/documents", tags=["documents"])

ExportFormat = Literal["json", "md", "html", "docx", "pdf", "tex"]


async def _authorize(project_id: uuid.UUID, db: AsyncSession) -> None:
    await ProjectService(db).get_project(project_id)


@router.post("/generate", response_model=GeneratedDocumentOut)
async def generate_document(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> GeneratedDocumentOut:
    """(Re)assembles the full document content from the latest Knowledge
    Graph, Requirements, and Security Engine state. Safe to call
    repeatedly — overwrites the previous version rather than duplicating."""
    await _authorize(project_id, db)
    return await DocumentGeneratorService(db).generate(project_id)  # type: ignore[return-value]


@router.get("", response_model=GeneratedDocumentOut)
async def get_document(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> GeneratedDocumentOut:
    await _authorize(project_id, db)
    return await DocumentGeneratorService(db).get_document(project_id)  # type: ignore[return-value]


@router.get("/export")
async def export_document(
    project_id: uuid.UUID,
    format: ExportFormat = "md",
    db: AsyncSession = Depends(get_db),
) -> Response:
    await _authorize(project_id, db)
    content_bytes, media_type, filename = await DocumentGeneratorService(db).export(
        project_id, format
    )
    return Response(
        content=content_bytes,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
