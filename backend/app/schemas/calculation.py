from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class CalculationCreate(BaseModel):
    input_json: dict = Field(default_factory=dict)
    currency: str = Field(default='RUB', max_length=10)


class CalculationOut(ORMBase):
    id: UUID
    company_id: UUID
    user_id: UUID
    input_json: dict
    result_json: dict
    currency: str
    total_amount: float
    created_at: datetime
