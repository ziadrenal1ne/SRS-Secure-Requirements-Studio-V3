import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.project import Project


class ReviewRun(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """One row per project, overwritten on each re-run — same pattern as
    SecurityAnalysis and GeneratedDocument.
    """

    __tablename__ = "review_runs"

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, unique=True
    )

    findings: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    rule_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    completeness_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    confidence_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    security_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    architecture_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    business_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    testing_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    overall_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    approved_for_export: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    project: Mapped["Project"] = relationship()
