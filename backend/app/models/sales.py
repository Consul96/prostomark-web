"""Sales data is separate from uploaded/AI documents and marking operations."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    LargeBinary,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, UUIDPKMixin


class SalesTenant(UUIDPKMixin, TimestampMixin):
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id"), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class SalesCustomer(Base, SalesTenant):
    __tablename__ = "sales_customers"
    kind: Mapped[str] = mapped_column(String(20))
    name: Mapped[str] = mapped_column(String(255), index=True)
    phone: Mapped[str | None] = mapped_column(String(40), index=True)
    inn: Mapped[str | None] = mapped_column(String(12), index=True)
    details: Mapped[dict] = mapped_column(JSONB, default=dict)
    archived: Mapped[bool] = mapped_column(Boolean, default=False)
    responsible_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    __table_args__ = (
        UniqueConstraint("company_id", "id"),
        CheckConstraint("kind in ('person','ip','legal')", name="sales_customer_kind"),
    )


class SalesSeller(Base, SalesTenant):
    __tablename__ = "sales_sellers"
    kind: Mapped[str] = mapped_column(String(20))
    name: Mapped[str] = mapped_column(String(255))
    inn: Mapped[str | None] = mapped_column(String(12))
    details: Mapped[dict] = mapped_column(JSONB, default=dict)
    vat_rules: Mapped[list] = mapped_column(JSONB, default=list)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    __table_args__ = (
        UniqueConstraint("company_id", "id"),
        CheckConstraint("kind in ('ip','legal')", name="sales_seller_kind"),
    )


class SalesOrder(Base, SalesTenant):
    __tablename__ = "sales_orders"
    number: Mapped[str] = mapped_column(String(40), index=True)
    order_date: Mapped[date] = mapped_column(Date, index=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sales_customers.id"), index=True
    )
    seller_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sales_sellers.id"), index=True
    )
    responsible_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    source: Mapped[str] = mapped_column(String(20), default="manual", index=True)
    status: Mapped[str] = mapped_column(String(20), default="draft", index=True)
    revision: Mapped[int] = mapped_column(Integer, default=1)
    delivery_address: Mapped[str] = mapped_column(String(2000), default="")
    comment: Mapped[str] = mapped_column(String(4000), default="")
    basis: Mapped[str] = mapped_column(String(1000), default="")
    vat_included: Mapped[bool] = mapped_column(Boolean, default=True)
    total: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    vat_total: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    discount_total: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    items = relationship(
        "SalesOrderItem",
        cascade="all, delete-orphan",
        primaryjoin="SalesOrder.id == SalesOrderItem.order_id",
        order_by="SalesOrderItem.position",
    )
    __table_args__ = (
        UniqueConstraint("company_id", "number"),
        UniqueConstraint("company_id", "id"),
        ForeignKeyConstraint(
            ["company_id", "seller_id"],
            ["sales_sellers.company_id", "sales_sellers.id"],
            name="sales_order_seller_tenant",
        ),
        ForeignKeyConstraint(
            ["company_id", "customer_id"],
            ["sales_customers.company_id", "sales_customers.id"],
            name="sales_order_customer_tenant",
        ),
        CheckConstraint(
            "status in ('draft','confirmed','completed','cancelled')",
            name="sales_order_status",
        ),
    )


class SalesOrderItem(Base, SalesTenant):
    __tablename__ = "sales_order_items"
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sales_orders.id", ondelete="CASCADE"),
        index=True,
    )
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="SET NULL")
    )
    position: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(255))
    article: Mapped[str | None] = mapped_column(String(120))
    gtin: Mapped[str | None] = mapped_column(String(64))
    unit: Mapped[str] = mapped_column(String(40))
    okei: Mapped[str] = mapped_column(String(10), default="796")
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 3))
    price: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    discount: Mapped[Decimal] = mapped_column(Numeric(7, 4))
    vat_rate: Mapped[Decimal | None] = mapped_column(Numeric(7, 4))
    total: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    vat_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    __table_args__ = (
        ForeignKeyConstraint(
            ["company_id", "order_id"],
            ["sales_orders.company_id", "sales_orders.id"],
            name="sales_item_order_tenant",
        ),
        CheckConstraint(
            "quantity > 0 AND price >= 0 AND discount >= 0 AND discount <= 100",
            name="sales_item_values",
        ),
    )


class SalesDocumentTemplate(Base, SalesTenant):
    __tablename__ = "sales_document_templates"
    # System templates have no company; account templates are scoped as usual.
    company_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True, index=True
    )
    document_type: Mapped[str] = mapped_column(String(30))
    name: Mapped[str] = mapped_column(String(255))
    version: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(30), default="active")
    fields: Mapped[dict] = mapped_column(JSONB, default=dict)


class SalesDocument(Base, SalesTenant):
    __tablename__ = "sales_documents"
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sales_orders.id"), index=True
    )
    seller_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sales_sellers.id")
    )
    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sales_document_templates.id")
    )
    document_type: Mapped[str] = mapped_column(String(30))
    number: Mapped[int] = mapped_column(Integer)
    year: Mapped[int] = mapped_column(Integer)
    document_date: Mapped[date] = mapped_column(Date)
    version: Mapped[int] = mapped_column(Integer)
    order_revision: Mapped[int] = mapped_column(Integer)
    idempotency_key: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    request_json: Mapped[dict] = mapped_column(JSONB)
    snapshot: Mapped[dict] = mapped_column(JSONB)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    __table_args__ = (
        UniqueConstraint("company_id", "idempotency_key"),
        UniqueConstraint("company_id", "id"),
        ForeignKeyConstraint(
            ["company_id", "order_id"],
            ["sales_orders.company_id", "sales_orders.id"],
            name="sales_document_order_tenant",
        ),
        ForeignKeyConstraint(
            ["company_id", "seller_id"],
            ["sales_sellers.company_id", "sales_sellers.id"],
            name="sales_document_seller_tenant",
        ),
        UniqueConstraint("seller_id", "document_type", "year", "number", "version"),
    )


class SalesDocumentFile(Base, SalesTenant):
    __tablename__ = "sales_document_files"
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sales_documents.id", ondelete="CASCADE"),
        index=True,
    )
    format: Mapped[str] = mapped_column(String(8))
    sha256: Mapped[str] = mapped_column(String(64))
    size: Mapped[int] = mapped_column(Integer)
    # Atomic storage with document transaction, no filesystem paths in the API.
    content: Mapped[bytes] = mapped_column(LargeBinary)
    __table_args__ = (
        UniqueConstraint("document_id", "format"),
        ForeignKeyConstraint(
            ["company_id", "document_id"],
            ["sales_documents.company_id", "sales_documents.id"],
            name="sales_file_document_tenant",
        ),
    )


class SalesDocumentSequence(Base, SalesTenant):
    __tablename__ = "sales_document_sequences"
    seller_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sales_sellers.id")
    )
    document_type: Mapped[str] = mapped_column(String(30))
    year: Mapped[int] = mapped_column(Integer)
    value: Mapped[int] = mapped_column(Integer, default=0)
    __table_args__ = (
        UniqueConstraint("seller_id", "document_type", "year"),
        ForeignKeyConstraint(
            ["company_id", "seller_id"],
            ["sales_sellers.company_id", "sales_sellers.id"],
            name="sales_sequence_seller_tenant",
        ),
    )
