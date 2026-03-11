import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPKMixin


class Product(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = 'products'

    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    brand: Mapped[str | None] = mapped_column(String(255), nullable=True)
    gtin: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    article: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)

    company = relationship('Company', back_populates='products')
    documents = relationship('Document', back_populates='product')
