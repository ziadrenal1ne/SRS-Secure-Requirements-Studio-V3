import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

ProjectStatus = Literal["brouillon", "en_cours", "en_revue", "valide"]


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=300)
    short_name: str = Field(min_length=1, max_length=120)
    department: str = ""
    description: str = ""


class ProjectUpdate(BaseModel):
    name: str | None = None
    short_name: str | None = None
    department: str | None = None
    description: str | None = None
    status: ProjectStatus | None = None
    progress: int | None = Field(default=None, ge=0, le=100)
    security_score: int | None = Field(default=None, ge=0, le=100)


class ProjectOut(BaseModel):
    id: uuid.UUID
    name: str
    short_name: str
    department: str
    description: str
    status: ProjectStatus
    progress: int
    security_score: int
    organization_id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
