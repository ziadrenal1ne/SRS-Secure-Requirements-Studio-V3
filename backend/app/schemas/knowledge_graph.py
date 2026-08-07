import uuid
from datetime import datetime

from pydantic import BaseModel


class KnowledgeGraphNodeOut(BaseModel):
    id: uuid.UUID
    concept_key: str
    domain: str
    label: str
    description: str
    completion: int
    confidence: int
    importance: str
    business_value: int
    risk: str
    status: str
    validation_rules: list[str]
    missing_information: list[str]
    captured_data: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class KnowledgeGraphEdgeOut(BaseModel):
    node_id: uuid.UUID
    dependency_node_id: uuid.UUID

    model_config = {"from_attributes": True}


class KnowledgeGraphOut(BaseModel):
    nodes: list[KnowledgeGraphNodeOut]
    edges: list[KnowledgeGraphEdgeOut]


class DomainCompletion(BaseModel):
    total: int
    completed: int


class ProjectCompletionOut(BaseModel):
    total_concepts: int
    completed_concepts: int
    overall_completion: float
    overall_confidence: float
    by_domain: dict[str, DomainCompletion]
