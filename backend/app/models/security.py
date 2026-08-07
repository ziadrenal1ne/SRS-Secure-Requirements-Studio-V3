import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.project import Project


class SecurityAnalysis(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """One row per project, overwritten on each (re)analysis. Kept as a
    single row rather than an append-only log for Phase 5 — Phase 9's
    Review Engine can extend this to versioned history if needed.
    """

    __tablename__ = "security_analyses"

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, unique=True
    )

    threat_model: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    rbac_matrix: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    risk_register: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    security_checklist: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    privacy_impact_assessment: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    data_classification: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    security_score: Mapped[int] = mapped_column(nullable=False, default=0)  # 0-100

    project: Mapped["Project"] = relationship()
