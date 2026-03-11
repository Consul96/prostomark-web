import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPKMixin
from app.models.enums import SubscriptionStatus


class SubscriptionPlan(Base, UUIDPKMixin):
    __tablename__ = 'subscription_plans'

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    code: Mapped[str] = mapped_column(String(80), nullable=False, unique=True, index=True)
    price_month: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    price_year: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    features_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    subscriptions = relationship('CompanySubscription', back_populates='plan')


class CompanySubscription(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = 'company_subscriptions'

    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True)
    plan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('subscription_plans.id'), nullable=False)
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    status: Mapped[SubscriptionStatus] = mapped_column(Enum(SubscriptionStatus, name='subscription_status_enum'), nullable=False, default=SubscriptionStatus.TRIAL)
    current_period_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    current_period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    company = relationship('Company', back_populates='subscriptions')
    plan = relationship('SubscriptionPlan', back_populates='subscriptions')
