from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    message: str


class AuditLogOut(ORMBase):
    id: UUID
    company_id: UUID | None
    user_id: UUID | None
    action: str
    entity_type: str
    entity_id: str | None
    meta_json: dict
    created_at: datetime
