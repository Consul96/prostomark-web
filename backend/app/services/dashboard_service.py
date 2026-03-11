from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.crud.audit_log import list_logs
from app.crud.subscription import get_active_company_subscription
from app.models.calculation import Calculation
from app.models.document import Document
from app.models.enums import UserRole
from app.models.product import Product
from app.models.user import User
from app.schemas.dashboard import DashboardAnalytics, DashboardSummaryOut


def get_dashboard_summary(db: Session, current_user: User) -> DashboardSummaryOut:
    product_stmt = select(func.count(Product.id))
    document_stmt = select(func.count(Document.id))
    calculation_stmt = select(func.count(Calculation.id))

    if current_user.role != UserRole.SUPERADMIN:
        product_stmt = product_stmt.where(Product.company_id == current_user.company_id)
        document_stmt = document_stmt.where(Document.company_id == current_user.company_id)
        calculation_stmt = calculation_stmt.where(Calculation.company_id == current_user.company_id)

    products_count = db.execute(product_stmt).scalar_one()
    documents_count = db.execute(document_stmt).scalar_one()
    calculations_count = db.execute(calculation_stmt).scalar_one()

    subscription_status = 'n/a'
    if current_user.role != UserRole.SUPERADMIN:
        subscription = get_active_company_subscription(db, current_user.company_id)
        if subscription:
            subscription_status = str(subscription.status)

    logs_company_id = None if current_user.role == UserRole.SUPERADMIN else str(current_user.company_id)
    recent_logs = list_logs(db, company_id=logs_company_id, limit=5, offset=0)

    status_stmt = select(Document.status, func.count(Document.id)).group_by(Document.status)
    if current_user.role != UserRole.SUPERADMIN:
        status_stmt = status_stmt.where(Document.company_id == current_user.company_id)
    status_rows = db.execute(status_stmt).all()

    seven_days_ago = datetime.now(UTC) - timedelta(days=7)
    calc_7d_stmt = select(func.count(Calculation.id)).where(Calculation.created_at >= seven_days_ago)
    if current_user.role != UserRole.SUPERADMIN:
        calc_7d_stmt = calc_7d_stmt.where(Calculation.company_id == current_user.company_id)

    calculations_last_7d = db.execute(calc_7d_stmt).scalar_one()

    analytics = DashboardAnalytics(
        documents_by_status={str(status): count for status, count in status_rows},
        calculations_last_7d=calculations_last_7d,
    )

    return DashboardSummaryOut(
        products_count=products_count,
        documents_count=documents_count,
        calculations_count=calculations_count,
        subscription_status=subscription_status,
        recent_actions=recent_logs,
        analytics=analytics,
    )
