from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import DocumentStatus
from app.schemas.common import ORMBase


class DocumentCreateMeta(BaseModel):
    product_id: UUID | None = None
    document_type: str = Field(default='other', max_length=120)
    number: str | None = Field(default=None, max_length=120)
    document_date: date | None = None


class DocumentOut(ORMBase):
    id: UUID
    company_id: UUID
    product_id: UUID | None
    document_type: str
    number: str | None
    document_date: date | None
    file_path: str
    original_filename: str
    mime_type: str
    status: DocumentStatus
    extracted_text: str | None
    ai_summary: str | None
    created_by: UUID
    created_at: datetime
