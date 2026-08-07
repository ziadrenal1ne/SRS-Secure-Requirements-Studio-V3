"""Import every model here so Base.metadata sees them all
(required for Alembic autogenerate and for create_all in tests).
"""
from app.models.base import Base
from app.models.generated_document import GeneratedDocument
from app.models.interview import InterviewSession, InterviewTurn
from app.models.knowledge_graph import KnowledgeGraphEdge, KnowledgeGraphNode
from app.models.organization import Membership, Organization
from app.models.project import Project
from app.models.requirement import Requirement
from app.models.review import ReviewRun
from app.models.security import SecurityAnalysis
from app.models.user import User

__all__ = [
    "Base",
    "GeneratedDocument",
    "InterviewSession",
    "InterviewTurn",
    "KnowledgeGraphEdge",
    "KnowledgeGraphNode",
    "Membership",
    "Organization",
    "Project",
    "Requirement",
    "ReviewRun",
    "SecurityAnalysis",
    "User",
]
