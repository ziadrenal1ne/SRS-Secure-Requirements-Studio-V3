import uuid
from datetime import datetime

from pydantic import BaseModel


class SecurityAnalysisOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    threat_model: list[dict]
    rbac_matrix: dict
    risk_register: list[dict]
    security_checklist: list[dict]
    privacy_impact_assessment: dict
    data_classification: list[dict]
    security_score: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
