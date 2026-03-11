import uuid

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPKMixin


class Calculation(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = 'calculations'

    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    input_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    result_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default='RUB')
    total_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)

    company = relationship('Company', back_populates='calculations')
    user = relationship('User', back_populates='calculations')
