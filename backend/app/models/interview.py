import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.project import Project

INTERVIEW_STATUSES = ("active", "paused", "completed")


class InterviewSession(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "interview_sessions"

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    # The concept_key of the question currently awaiting an answer, if any.
    # Enables resume: the frontend just re-fetches state instead of the
    # engine having to recompute "what was I about to ask".
    pending_concept_key: Mapped[str | None] = mapped_column(String(150), nullable=True)
    pending_question: Mapped[str | None] = mapped_column(Text, nullable=True)

    project: Mapped["Project"] = relationship()
    turns: Mapped[list["InterviewTurn"]] = relationship(
        back_populates="session", cascade="all, delete-orphan", order_by="InterviewTurn.sequence"
    )


class InterviewTurn(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "interview_turns"

    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    concept_key: Mapped[str] = mapped_column(String(150), nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    completion_delta: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    confidence_delta: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    consultant_note: Mapped[str] = mapped_column(Text, nullable=False, default="")
    extracted_data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    session: Mapped["InterviewSession"] = relationship(back_populates="turns")
