from pydantic import BaseModel, Field

from app.schemas.company import CompanySubscriptionOut, PlanOut


class CheckoutRequest(BaseModel):
    plan_code: str = Field(min_length=2, max_length=80)
    billing_cycle: str = Field(default='month', pattern='^(month|year)$')


class CheckoutResponse(BaseModel):
    checkout_url: str
    session_id: str


class CurrentPlanResponse(BaseModel):
    subscription: CompanySubscriptionOut | None
    available_plans: list[PlanOut]
