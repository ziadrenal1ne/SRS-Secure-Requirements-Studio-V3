import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class InterviewTurnOut(BaseModel):
    sequence: int
    concept_key: str
    question: str
    answer: str
    completion_delta: int
    confidence_delta: int
    consultant_note: str
    extracted_data: dict = Field(default_factory=dict)
    created_at: datetime

    model_config = {"from_attributes": True}


class InterviewSessionOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    status: str
    pending_question: str | None
    pending_concept_key: str | None
    pending_question_options: list[str] = Field(default_factory=list)
    pending_section: str | None = None
    max_questions: int = 20
    turns: list[InterviewTurnOut]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AnswerRequest(BaseModel):
    answer: str = Field(min_length=1, max_length=5000)


class AnswerResponse(BaseModel):
    concept_key: str
    consultant_note: str
    next_question: str | None
    next_concept_key: str | None
    next_question_options: list[str] = Field(default_factory=list)
    next_section: str | None = None
    max_questions: int = 20
    generated_document_id: uuid.UUID | None = None
    interview_status: str
