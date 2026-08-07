import uuid

from pydantic import BaseModel


class OrganizationMemberOut(BaseModel):
    user_id: uuid.UUID
    email: str
    full_name: str
    role: str

    model_config = {"from_attributes": True}
