from pydantic import BaseModel

from app.schemas.common import AuditLogOut


class DashboardAnalytics(BaseModel):
    documents_by_status: dict[str, int]
    calculations_last_7d: int


class DashboardSummaryOut(BaseModel):
    products_count: int
    documents_count: int
    calculations_count: int
    subscription_status: str
    recent_actions: list[AuditLogOut]
    analytics: DashboardAnalytics
