import uuid
from typing import TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.project import Project

KG_DOMAINS = (
    "business", "stakeholders", "users", "beneficiaries", "roles", "permissions",
    "entities", "database", "api", "security", "deployment", "testing",
    "training", "monitoring", "compliance",
)
KG_IMPORTANCE = ("low", "medium", "high", "critical")
KG_STATUS = ("not_started", "in_progress", "completed", "validated")


class KnowledgeGraphNode(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """One concept the system needs to understand about a project.

    Nodes are instantiated per-project from the concept catalog
    (app/domain/concept_catalog.py) at project creation, so completion,
    confidence, and captured data are tracked independently per project
    while the ontology itself (which concepts exist, how they relate)
    stays centrally defined and versionable.
    """

    __tablename__ = "knowledge_graph_nodes"
    __table_args__ = (
        UniqueConstraint("project_id", "concept_key", name="uq_kg_node_project_concept"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    concept_key: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    domain: Mapped[str] = mapped_column(String(30), nullable=False)
    label: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")

    completion: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # 0-100
    confidence: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # 0-100
    importance: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    business_value: Mapped[int] = mapped_column(Integer, nullable=False, default=50)  # 0-100
    risk: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="not_started")

    validation_rules: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    missing_information: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    captured_data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    generated_questions: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    project: Mapped["Project"] = relationship()


class KnowledgeGraphEdge(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A directed 'depends_on' edge: node depends_on dependency_node
    (dependency should reach reasonable completion before node is asked about).
    """

    __tablename__ = "knowledge_graph_edges"
    __table_args__ = (
        UniqueConstraint("node_id", "dependency_node_id", name="uq_kg_edge_pair"),
    )

    node_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("knowledge_graph_nodes.id", ondelete="CASCADE"), nullable=False
    )
    dependency_node_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("knowledge_graph_nodes.id", ondelete="CASCADE"), nullable=False
    )
