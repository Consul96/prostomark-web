import uuid
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPKMixin
from app.models.enums import DocumentStatus


class Document(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = 'documents'

    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True)
    product_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey('products.id', ondelete='SET NULL'), nullable=True, index=True)
    document_type: Mapped[str] = mapped_column(String(120), nullable=False)
    number: Mapped[str | None] = mapped_column(String(120), nullable=True)
    document_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[DocumentStatus] = mapped_column(Enum(DocumentStatus, name='document_status_enum'), nullable=False, default=DocumentStatus.UPLOADED)
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)

    company = relationship('Company', back_populates='documents')
    product = relationship('Product', back_populates='documents')
