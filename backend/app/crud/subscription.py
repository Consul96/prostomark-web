import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.subscription import CompanySubscription, SubscriptionPlan


def get_active_company_subscription(db: Session, company_id: uuid.UUID) -> CompanySubscription | None:
    stmt = (
        select(CompanySubscription)
        .where(CompanySubscription.company_id == company_id)
        .order_by(CompanySubscription.created_at.desc())
        .options(joinedload(CompanySubscription.plan))
    )
    return db.execute(stmt).scalars().first()


def get_subscription_by_stripe_id(db: Session, stripe_subscription_id: str) -> CompanySubscription | None:
    stmt = select(CompanySubscription).where(CompanySubscription.stripe_subscription_id == stripe_subscription_id)
    return db.execute(stmt).scalar_one_or_none()


def list_subscriptions(db: Session, *, limit: int = 50, offset: int = 0) -> list[CompanySubscription]:
    stmt = (
        select(CompanySubscription)
        .options(joinedload(CompanySubscription.plan))
        .order_by(CompanySubscription.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(db.execute(stmt).scalars().all())


def list_plans(db: Session, only_active: bool = True) -> list[SubscriptionPlan]:
    stmt = select(SubscriptionPlan).order_by(SubscriptionPlan.price_month.asc())
    if only_active:
        stmt = stmt.where(SubscriptionPlan.is_active.is_(True))
    return list(db.execute(stmt).scalars().all())


def get_plan_by_code(db: Session, code: str) -> SubscriptionPlan | None:
    stmt = select(SubscriptionPlan).where(SubscriptionPlan.code == code, SubscriptionPlan.is_active.is_(True))
    return db.execute(stmt).scalar_one_or_none()
