import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.project import Project

REQUIREMENT_PRIORITIES = ("low", "medium", "high", "critical")
REQUIREMENT_STATUSES = ("draft", "proposed", "approved", "implemented", "verified")
REQUIREMENT_RISKS = ("low", "medium", "high", "critical")


class Requirement(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "requirements"
    __table_args__ = (
        UniqueConstraint("project_id", "requirement_key", name="uq_requirement_project_key"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )

    # Human-readable traceable ID, e.g. "BR-001", "SEC-004".
    requirement_key: Mapped[str] = mapped_column(String(20), nullable=False)
    requirement_type: Mapped[str] = mapped_column(String(30), nullable=False)

    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    business_goal: Mapped[str] = mapped_column(Text, nullable=False, default="")
    risk: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    owner: Mapped[str] = mapped_column(String(200), nullable=False, default="")

    actors: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    acceptance_criteria: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    dependencies: Mapped[list] = mapped_column(JSON, nullable=False, default=list)  # requirement_keys
    security_controls: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    database_tables: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    api_endpoints: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    ui_screens: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    test_cases: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    # Traceability back to the Knowledge Graph concept this requirement was
    # derived from — this is what makes "everything must be traceable" real
    # rather than aspirational.
    source_concept_key: Mapped[str] = mapped_column(String(150), nullable=False)

    project: Mapped["Project"] = relationship()
