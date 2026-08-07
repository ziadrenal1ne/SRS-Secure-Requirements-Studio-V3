import uuid
from datetime import datetime

from pydantic import BaseModel


class ReviewFindingOut(BaseModel):
    rule_id: str
    category: str
    severity: str
    target: str
    message: str
    passed: bool


class ReviewRunOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    findings: list[ReviewFindingOut]
    rule_count: int
    failed_count: int
    completeness_score: int
    confidence_score: int
    security_score: int
    architecture_score: int
    business_score: int
    testing_score: int
    overall_score: int
    approved_for_export: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
