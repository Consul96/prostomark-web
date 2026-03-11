from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    brand: str | None = Field(default=None, max_length=255)
    gtin: str | None = Field(default=None, max_length=64)
    article: str | None = Field(default=None, max_length=120)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    brand: str | None = Field(default=None, max_length=255)
    gtin: str | None = Field(default=None, max_length=64)
    article: str | None = Field(default=None, max_length=120)


class ProductOut(ORMBase):
    id: UUID
    company_id: UUID
    name: str
    brand: str | None
    gtin: str | None
    article: str | None
    created_by: UUID
    created_at: datetime
