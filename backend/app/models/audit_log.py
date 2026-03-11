import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPKMixin


class AuditLog(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = 'audit_logs'

    company_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey('companies.id', ondelete='SET NULL'), nullable=True, index=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(120), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    meta_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    user = relationship('User', back_populates='audit_logs')
