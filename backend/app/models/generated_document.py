import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.project import Project


class GeneratedDocument(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """One row per project, overwritten on each (re)generation — same
    pattern as SecurityAnalysis. Stores the assembled content dict;
    export formats are rendered on demand from this, not pre-rendered
    and stored, so a re-export always reflects the latest content
    without needing to regenerate first.
    """

    __tablename__ = "generated_documents"

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    content: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    project: Mapped["Project"] = relationship()
