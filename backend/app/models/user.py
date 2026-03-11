import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPKMixin
from app.models.enums import UserRole


class User(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = 'users'

    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(120), nullable=False)
    last_name: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name='user_role_enum'), default=UserRole.USER, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    company = relationship('Company', back_populates='users')
    calculations = relationship('Calculation', back_populates='user')
    audit_logs = relationship('AuditLog', back_populates='user')
    refresh_tokens = relationship('RefreshToken', back_populates='user')
