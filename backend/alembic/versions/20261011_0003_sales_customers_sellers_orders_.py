"""sales customers sellers orders immutable documents

Revision ID: 20261011_0003
Revises: 20260716_0002
Create Date: 2026-10-11 18:49:06.038188

"""

from uuid import UUID
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20261011_0003"
down_revision = "20260716_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sales_document_templates",
        sa.Column("company_id", sa.UUID(), nullable=True),
        sa.Column("document_type", sa.String(length=30), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("fields", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_sales_document_templates_company_id"),
        "sales_document_templates",
        ["company_id"],
        unique=False,
    )
    op.create_table(
        "sales_sellers",
        sa.Column("kind", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("inn", sa.String(length=12), nullable=True),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("vat_rules", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("kind in ('ip','legal')", name="sales_seller_kind"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_sales_sellers_company_id"),
        "sales_sellers",
        ["company_id"],
        unique=False,
    )
    op.create_table(
        "sales_customers",
        sa.Column("kind", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=40), nullable=True),
        sa.Column("inn", sa.String(length=12), nullable=True),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("archived", sa.Boolean(), nullable=False),
        sa.Column("responsible_id", sa.UUID(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "kind in ('person','ip','legal')", name="sales_customer_kind"
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["responsible_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_sales_customers_company_id"),
        "sales_customers",
        ["company_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_sales_customers_inn"), "sales_customers", ["inn"], unique=False
    )
    op.create_index(
        op.f("ix_sales_customers_name"), "sales_customers", ["name"], unique=False
    )
    op.create_index(
        op.f("ix_sales_customers_phone"), "sales_customers", ["phone"], unique=False
    )
    op.create_table(
        "sales_document_sequences",
        sa.Column("seller_id", sa.UUID(), nullable=False),
        sa.Column("document_type", sa.String(length=30), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("value", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["seller_id"], ["sales_sellers.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("seller_id", "document_type", "year"),
    )
    op.create_index(
        op.f("ix_sales_document_sequences_company_id"),
        "sales_document_sequences",
        ["company_id"],
        unique=False,
    )
    op.create_table(
        "sales_orders",
        sa.Column("number", sa.String(length=40), nullable=False),
        sa.Column("order_date", sa.Date(), nullable=False),
        sa.Column("customer_id", sa.UUID(), nullable=False),
        sa.Column("seller_id", sa.UUID(), nullable=False),
        sa.Column("responsible_id", sa.UUID(), nullable=False),
        sa.Column("source", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("delivery_address", sa.String(length=2000), nullable=False),
        sa.Column("comment", sa.String(length=4000), nullable=False),
        sa.Column("basis", sa.String(length=1000), nullable=False),
        sa.Column("vat_included", sa.Boolean(), nullable=False),
        sa.Column("total", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("vat_total", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("discount_total", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status in ('draft','confirmed','completed','cancelled')",
            name="sales_order_status",
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["customer_id"], ["sales_customers.id"]),
        sa.ForeignKeyConstraint(["responsible_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["seller_id"], ["sales_sellers.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("company_id", "number"),
    )
    op.create_index(
        op.f("ix_sales_orders_company_id"), "sales_orders", ["company_id"], unique=False
    )
    op.create_index(
        op.f("ix_sales_orders_customer_id"),
        "sales_orders",
        ["customer_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_sales_orders_number"), "sales_orders", ["number"], unique=False
    )
    op.create_index(
        op.f("ix_sales_orders_order_date"), "sales_orders", ["order_date"], unique=False
    )
    op.create_index(
        op.f("ix_sales_orders_responsible_id"),
        "sales_orders",
        ["responsible_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_sales_orders_seller_id"), "sales_orders", ["seller_id"], unique=False
    )
    op.create_index(
        op.f("ix_sales_orders_source"), "sales_orders", ["source"], unique=False
    )
    op.create_index(
        op.f("ix_sales_orders_status"), "sales_orders", ["status"], unique=False
    )
    op.create_table(
        "sales_documents",
        sa.Column("order_id", sa.UUID(), nullable=False),
        sa.Column("seller_id", sa.UUID(), nullable=False),
        sa.Column("template_id", sa.UUID(), nullable=False),
        sa.Column("document_type", sa.String(length=30), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("document_date", sa.Date(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("order_revision", sa.Integer(), nullable=False),
        sa.Column("idempotency_key", sa.UUID(), nullable=False),
        sa.Column(
            "request_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column("snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["order_id"], ["sales_orders.id"]),
        sa.ForeignKeyConstraint(["seller_id"], ["sales_sellers.id"]),
        sa.ForeignKeyConstraint(["template_id"], ["sales_document_templates.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("company_id", "idempotency_key"),
        sa.UniqueConstraint("seller_id", "document_type", "year", "number", "version"),
    )
    op.create_index(
        op.f("ix_sales_documents_company_id"),
        "sales_documents",
        ["company_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_sales_documents_order_id"),
        "sales_documents",
        ["order_id"],
        unique=False,
    )
    op.create_table(
        "sales_order_items",
        sa.Column("order_id", sa.UUID(), nullable=False),
        sa.Column("product_id", sa.UUID(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("article", sa.String(length=120), nullable=True),
        sa.Column("gtin", sa.String(length=64), nullable=True),
        sa.Column("unit", sa.String(length=40), nullable=False),
        sa.Column("okei", sa.String(length=10), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=18, scale=3), nullable=False),
        sa.Column("price", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("discount", sa.Numeric(precision=7, scale=4), nullable=False),
        sa.Column("vat_rate", sa.Numeric(precision=7, scale=4), nullable=True),
        sa.Column("total", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("vat_amount", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "quantity > 0 AND price >= 0 AND discount >= 0 AND discount <= 100",
            name="sales_item_values",
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["order_id"], ["sales_orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_sales_order_items_company_id"),
        "sales_order_items",
        ["company_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_sales_order_items_order_id"),
        "sales_order_items",
        ["order_id"],
        unique=False,
    )
    op.create_table(
        "sales_document_files",
        sa.Column("document_id", sa.UUID(), nullable=False),
        sa.Column("format", sa.String(length=8), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("size", sa.Integer(), nullable=False),
        sa.Column("content", sa.LargeBinary(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(
            ["document_id"], ["sales_documents.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("document_id", "format"),
    )
    op.create_index(
        op.f("ix_sales_document_files_company_id"),
        "sales_document_files",
        ["company_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_sales_document_files_document_id"),
        "sales_document_files",
        ["document_id"],
        unique=False,
    )

    op.create_unique_constraint(
        "uq_sales_customers_tenant_id", "sales_customers", ["company_id", "id"]
    )
    op.create_unique_constraint(
        "uq_sales_sellers_tenant_id", "sales_sellers", ["company_id", "id"]
    )
    op.create_unique_constraint(
        "uq_sales_orders_tenant_id", "sales_orders", ["company_id", "id"]
    )
    op.create_unique_constraint(
        "uq_sales_documents_tenant_id", "sales_documents", ["company_id", "id"]
    )
    op.create_foreign_key(
        "sales_order_seller_tenant",
        "sales_orders",
        "sales_sellers",
        ["company_id", "seller_id"],
        ["company_id", "id"],
    )
    op.create_foreign_key(
        "sales_order_customer_tenant",
        "sales_orders",
        "sales_customers",
        ["company_id", "customer_id"],
        ["company_id", "id"],
    )
    op.create_foreign_key(
        "sales_item_order_tenant",
        "sales_order_items",
        "sales_orders",
        ["company_id", "order_id"],
        ["company_id", "id"],
    )
    op.create_foreign_key(
        "sales_document_order_tenant",
        "sales_documents",
        "sales_orders",
        ["company_id", "order_id"],
        ["company_id", "id"],
    )
    op.create_foreign_key(
        "sales_document_seller_tenant",
        "sales_documents",
        "sales_sellers",
        ["company_id", "seller_id"],
        ["company_id", "id"],
    )
    op.create_foreign_key(
        "sales_file_document_tenant",
        "sales_document_files",
        "sales_documents",
        ["company_id", "document_id"],
        ["company_id", "id"],
    )
    op.create_foreign_key(
        "sales_sequence_seller_tenant",
        "sales_document_sequences",
        "sales_sellers",
        ["company_id", "seller_id"],
        ["company_id", "id"],
    )

    templates = sa.table(
        "sales_document_templates",
        sa.column("id", sa.UUID()),
        sa.column("company_id", sa.UUID()),
        sa.column("document_type", sa.String()),
        sa.column("name", sa.String()),
        sa.column("version", sa.Integer()),
        sa.column("status", sa.String()),
        sa.column("fields", postgresql.JSONB()),
    )
    op.bulk_insert(
        templates,
        [
            {
                "id": UUID("ef061991-c930-4cde-90be-1ba07eaf1001"),
                "company_id": None,
                "document_type": "torg12",
                "name": "ТОРГ-12 (стартовая печатная форма)",
                "version": 1,
                "status": "active",
                "fields": {"renderer": "starter_v1"},
            },
            {
                "id": UUID("ef061991-c930-4cde-90be-1ba07eaf1002"),
                "company_id": None,
                "document_type": "upd",
                "name": "УПД (стартовая печатная форма)",
                "version": 1,
                "status": "active",
                "fields": {"renderer": "starter_v1"},
            },
            {
                "id": UUID("ef061991-c930-4cde-90be-1ba07eaf1003"),
                "company_id": None,
                "document_type": "invoice",
                "name": "Товарная накладная",
                "version": 1,
                "status": "active",
                "fields": {"renderer": "starter_v1"},
            },
        ],
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_sales_document_files_document_id"), table_name="sales_document_files"
    )
    op.drop_index(
        op.f("ix_sales_document_files_company_id"), table_name="sales_document_files"
    )
    op.drop_table("sales_document_files")
    op.drop_index(op.f("ix_sales_order_items_order_id"), table_name="sales_order_items")
    op.drop_index(
        op.f("ix_sales_order_items_company_id"), table_name="sales_order_items"
    )
    op.drop_table("sales_order_items")
    op.drop_index(op.f("ix_sales_documents_order_id"), table_name="sales_documents")
    op.drop_index(op.f("ix_sales_documents_company_id"), table_name="sales_documents")
    op.drop_table("sales_documents")
    op.drop_index(op.f("ix_sales_orders_status"), table_name="sales_orders")
    op.drop_index(op.f("ix_sales_orders_source"), table_name="sales_orders")
    op.drop_index(op.f("ix_sales_orders_seller_id"), table_name="sales_orders")
    op.drop_index(op.f("ix_sales_orders_responsible_id"), table_name="sales_orders")
    op.drop_index(op.f("ix_sales_orders_order_date"), table_name="sales_orders")
    op.drop_index(op.f("ix_sales_orders_number"), table_name="sales_orders")
    op.drop_index(op.f("ix_sales_orders_customer_id"), table_name="sales_orders")
    op.drop_index(op.f("ix_sales_orders_company_id"), table_name="sales_orders")
    op.drop_table("sales_orders")
    op.drop_index(
        op.f("ix_sales_document_sequences_company_id"),
        table_name="sales_document_sequences",
    )
    op.drop_table("sales_document_sequences")
    op.drop_index(op.f("ix_sales_customers_phone"), table_name="sales_customers")
    op.drop_index(op.f("ix_sales_customers_name"), table_name="sales_customers")
    op.drop_index(op.f("ix_sales_customers_inn"), table_name="sales_customers")
    op.drop_index(op.f("ix_sales_customers_company_id"), table_name="sales_customers")
    op.drop_table("sales_customers")
    op.drop_index(op.f("ix_sales_sellers_company_id"), table_name="sales_sellers")
    op.drop_table("sales_sellers")
    op.drop_index(
        op.f("ix_sales_document_templates_company_id"),
        table_name="sales_document_templates",
    )
    op.drop_table("sales_document_templates")
