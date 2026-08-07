import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel

RequirementPriority = Literal["low", "medium", "high", "critical"]
RequirementStatus = Literal["draft", "proposed", "approved", "implemented", "verified"]
RequirementRisk = Literal["low", "medium", "high", "critical"]


class RequirementOut(BaseModel):
    id: uuid.UUID
    requirement_key: str
    requirement_type: str
    title: str
    description: str
    priority: RequirementPriority
    business_goal: str
    risk: RequirementRisk
    status: RequirementStatus
    owner: str
    actors: list[str]
    acceptance_criteria: list[str]
    dependencies: list[str]
    security_controls: list[str]
    database_tables: list[str]
    api_endpoints: list[str]
    ui_screens: list[str]
    test_cases: list[str]
    source_concept_key: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RequirementUpdate(BaseModel):
    priority: RequirementPriority | None = None
    status: RequirementStatus | None = None
    owner: str | None = None
    title: str | None = None
    description: str | None = None


class TraceabilityMatrixRow(BaseModel):
    requirement_key: str
    requirement_type: str
    title: str
    priority: str
    status: str
    risk: str
    dependencies: list[str]
    security_controls: list[str]
    database_tables: list[str]
    api_endpoints: list[str]
    ui_screens: list[str]
    test_cases: list[str]
    source_concept_key: str
