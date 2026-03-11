from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPKMixin


class Company(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = 'companies'

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    users = relationship('User', back_populates='company')
    products = relationship('Product', back_populates='company')
    documents = relationship('Document', back_populates='company')
    calculations = relationship('Calculation', back_populates='company')
    subscriptions = relationship('CompanySubscription', back_populates='company')
