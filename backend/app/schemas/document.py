import uuid
from datetime import datetime

from pydantic import BaseModel


class GeneratedDocumentOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    content: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
