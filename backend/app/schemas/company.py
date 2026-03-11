from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.common import ORMBase


class CompanyOut(ORMBase):
    id: UUID
    name: str
    slug: str
    is_active: bool
    created_at: datetime


class PlanOut(ORMBase):
    id: UUID
    name: str
    code: str
    price_month: float
    price_year: float
    features_json: dict
    is_active: bool


class CompanySubscriptionOut(ORMBase):
    id: UUID
    company_id: UUID
    plan_id: UUID
    stripe_customer_id: str | None
    stripe_subscription_id: str | None
    status: str
    current_period_start: datetime | None
    current_period_end: datetime | None
    created_at: datetime
    plan: PlanOut
