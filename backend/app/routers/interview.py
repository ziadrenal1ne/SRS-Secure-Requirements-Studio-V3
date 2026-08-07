import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.interview import AnswerRequest, AnswerResponse, InterviewSessionOut
from app.services.interview import InterviewService
from app.services.project import ProjectService

router = APIRouter(prefix="/projects/{project_id}/interview", tags=["interview"])


@router.post("/start", response_model=InterviewSessionOut)
async def start_or_resume_interview(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> InterviewSessionOut:
    await ProjectService(db).get_project(project_id)
    service = InterviewService(db)
    session = await service.start_or_resume(project_id)
    return InterviewSessionOut.model_validate(session).model_copy(
        update=service.session_metadata(session)
    )


@router.post("/answer", response_model=AnswerResponse)
async def answer_question(
    project_id: uuid.UUID,
    payload: AnswerRequest,
    db: AsyncSession = Depends(get_db),
) -> AnswerResponse:
    await ProjectService(db).get_project(project_id)
    result = await InterviewService(db).submit_answer(project_id, payload.answer)
    return AnswerResponse(**{k: v for k, v in result.items() if k != "updated_node"})


@router.get("/state", response_model=InterviewSessionOut)
async def get_interview_state(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> InterviewSessionOut:
    await ProjectService(db).get_project(project_id)
    service = InterviewService(db)
    session = await service.get_state(project_id)
    return InterviewSessionOut.model_validate(session).model_copy(
        update=service.session_metadata(session)
    )
