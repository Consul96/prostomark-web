"""marking module (Честный знак) schema

Revision ID: 20260716_0002
Revises: 20260311_0001
Create Date: 2026-07-16
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '20260716_0002'
down_revision = '20260311_0001'
branch_labels = None
depends_on = None

UUID = postgresql.UUID(as_uuid=True)
JSONB = postgresql.JSONB


def _uuid_pk():
    return sa.Column('id', UUID, primary_key=True, nullable=False)


def _company():
    return sa.Column('company_id', UUID, sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)


def _created():
    return sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)


def _updated():
    return sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)


def upgrade() -> None:
    op.create_table(
        'marking_signer_agents',
        _uuid_pk(),
        _company(),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('api_key_hash', sa.String(128), nullable=False),
        sa.Column('certificate_thumbprint', sa.String(80)),
        sa.Column('certificate_subject', sa.String(512)),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('last_heartbeat_at', sa.DateTime(timezone=True)),
        sa.Column('version', sa.String(64)),
        _created(),
        _updated(),
    )
    op.create_index('ix_marking_signer_agents_company_id', 'marking_signer_agents', ['company_id'])
    op.create_index('ix_marking_signer_agents_api_key_hash', 'marking_signer_agents', ['api_key_hash'], unique=True)

    op.create_table(
        'marking_crpt_clients',
        _uuid_pk(),
        _company(),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('inn', sa.String(12), nullable=False),
        sa.Column('environment', sa.String(16), nullable=False, server_default='sandbox'),
        sa.Column('product_groups', JSONB, nullable=False, server_default='[]'),
        sa.Column('oms_id', sa.String(64)),
        sa.Column('oms_connection', sa.String(128)),
        sa.Column('timezone', sa.String(64), nullable=False, server_default='Europe/Moscow'),
        sa.Column('signer_agent_id', UUID, sa.ForeignKey('marking_signer_agents.id', ondelete='SET NULL')),
        sa.Column('signer_certificate_thumbprint', sa.String(80)),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('true_api_status', sa.String(24), nullable=False, server_default='unknown'),
        sa.Column('suz_status', sa.String(24), nullable=False, server_default='unknown'),
        sa.Column('mchd_status', sa.String(24), nullable=False, server_default='unknown'),
        sa.Column('mchd_number', sa.String(128)),
        sa.Column('mchd_valid_from', sa.Date()),
        sa.Column('mchd_valid_until', sa.Date()),
        sa.Column('last_connection_check_at', sa.DateTime(timezone=True)),
        sa.Column('settings', JSONB, nullable=False, server_default='{}'),
        _created(),
        _updated(),
        sa.UniqueConstraint('company_id', 'inn', 'environment', name='uq_crpt_client_company_inn_env'),
    )
    op.create_index('ix_marking_crpt_clients_company_id', 'marking_crpt_clients', ['company_id'])
    op.create_index('ix_marking_crpt_clients_inn', 'marking_crpt_clients', ['inn'])

    op.create_table(
        'marking_client_connection_checks',
        _uuid_pk(),
        _company(),
        sa.Column('crpt_client_id', UUID, sa.ForeignKey('marking_crpt_clients.id', ondelete='CASCADE'), nullable=False),
        sa.Column('kind', sa.String(24), nullable=False),
        sa.Column('status', sa.String(24), nullable=False),
        sa.Column('detail', sa.Text()),
        sa.Column('correlation_id', sa.String(64)),
        _created(),
    )
    op.create_index('ix_marking_conn_checks_company', 'marking_client_connection_checks', ['company_id'])
    op.create_index('ix_marking_conn_checks_client', 'marking_client_connection_checks', ['crpt_client_id'])

    op.create_table(
        'marking_mchd_access_profiles',
        _uuid_pk(),
        _company(),
        sa.Column('crpt_client_id', UUID, sa.ForeignKey('marking_crpt_clients.id', ondelete='CASCADE'), nullable=False),
        sa.Column('signer_agent_id', UUID, sa.ForeignKey('marking_signer_agents.id', ondelete='SET NULL')),
        sa.Column('signer_certificate_thumbprint', sa.String(80)),
        sa.Column('signer_inn', sa.String(12)),
        sa.Column('mchd_number', sa.String(128)),
        sa.Column('mchd_valid_from', sa.Date()),
        sa.Column('mchd_valid_until', sa.Date()),
        sa.Column('status', sa.String(24), nullable=False, server_default='unknown'),
        sa.Column('product_groups', JSONB, nullable=False, server_default='[]'),
        _created(),
        _updated(),
    )
    op.create_index('ix_marking_mchd_company', 'marking_mchd_access_profiles', ['company_id'])
    op.create_index('ix_marking_mchd_client', 'marking_mchd_access_profiles', ['crpt_client_id'])

    op.create_table(
        'marking_applications',
        _uuid_pk(),
        _company(),
        sa.Column('crpt_client_id', UUID, sa.ForeignKey('marking_crpt_clients.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('external_application_number', sa.String(64)),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('product_group', sa.String(24), nullable=False),
        sa.Column('workflow_type', sa.String(32)),
        sa.Column('release_method', sa.String(32)),
        sa.Column('status', sa.String(24), nullable=False, server_default='draft'),
        sa.Column('progress', JSONB, nullable=False, server_default='{}'),
        sa.Column('created_by', UUID, sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('assigned_to', UUID, sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('metadata', JSONB, nullable=False, server_default='{}'),
        _created(),
        _updated(),
    )
    op.create_index('ix_marking_applications_company', 'marking_applications', ['company_id'])
    op.create_index('ix_marking_applications_client', 'marking_applications', ['crpt_client_id'])
    op.create_index('ix_marking_applications_extnum', 'marking_applications', ['external_application_number'])

    op.create_table(
        'marking_product_cards',
        _uuid_pk(),
        _company(),
        sa.Column('crpt_client_id', UUID, sa.ForeignKey('marking_crpt_clients.id', ondelete='CASCADE'), nullable=False),
        sa.Column('application_id', UUID, sa.ForeignKey('marking_applications.id', ondelete='SET NULL')),
        sa.Column('product_id', UUID, sa.ForeignKey('products.id', ondelete='SET NULL')),
        sa.Column('product_group', sa.String(24), nullable=False),
        sa.Column('name', sa.String(512), nullable=False),
        sa.Column('article', sa.String(128)),
        sa.Column('brand', sa.String(255)),
        sa.Column('tnved', sa.String(16)),
        sa.Column('attributes', JSONB, nullable=False, server_default='{}'),
        sa.Column('gtin', sa.String(14)),
        sa.Column('good_id', sa.String(64)),
        sa.Column('nk_status', sa.String(24), nullable=False, server_default='draft'),
        sa.Column('errors', JSONB, nullable=False, server_default='[]'),
        _created(),
        _updated(),
    )
    op.create_index('ix_marking_cards_company', 'marking_product_cards', ['company_id'])
    op.create_index('ix_marking_cards_client', 'marking_product_cards', ['crpt_client_id'])
    op.create_index('ix_marking_cards_app', 'marking_product_cards', ['application_id'])
    op.create_index('ix_marking_cards_article', 'marking_product_cards', ['article'])
    op.create_index('ix_marking_cards_gtin', 'marking_product_cards', ['gtin'])

    op.create_table(
        'marking_nk_feeds',
        _uuid_pk(),
        _company(),
        sa.Column('crpt_client_id', UUID, sa.ForeignKey('marking_crpt_clients.id', ondelete='CASCADE'), nullable=False),
        sa.Column('application_id', UUID, sa.ForeignKey('marking_applications.id', ondelete='SET NULL')),
        sa.Column('external_feed_id', sa.String(64)),
        sa.Column('status', sa.String(24), nullable=False, server_default='draft'),
        sa.Column('payload', JSONB, nullable=False, server_default='{}'),
        sa.Column('result', JSONB, nullable=False, server_default='{}'),
        _created(),
        _updated(),
    )
    op.create_index('ix_marking_feeds_company', 'marking_nk_feeds', ['company_id'])
    op.create_index('ix_marking_feeds_client', 'marking_nk_feeds', ['crpt_client_id'])
    op.create_index('ix_marking_feeds_extid', 'marking_nk_feeds', ['external_feed_id'])

    op.create_table(
        'marking_nk_feed_items',
        _uuid_pk(),
        sa.Column('feed_id', UUID, sa.ForeignKey('marking_nk_feeds.id', ondelete='CASCADE'), nullable=False),
        sa.Column('product_card_id', UUID, sa.ForeignKey('marking_product_cards.id', ondelete='SET NULL')),
        sa.Column('gtin', sa.String(14)),
        sa.Column('status', sa.String(24), nullable=False, server_default='draft'),
        sa.Column('errors', JSONB, nullable=False, server_default='[]'),
        _created(),
    )
    op.create_index('ix_marking_feed_items_feed', 'marking_nk_feed_items', ['feed_id'])

    op.create_table(
        'marking_km_orders',
        _uuid_pk(),
        _company(),
        sa.Column('crpt_client_id', UUID, sa.ForeignKey('marking_crpt_clients.id', ondelete='CASCADE'), nullable=False),
        sa.Column('application_id', UUID, sa.ForeignKey('marking_applications.id', ondelete='SET NULL')),
        sa.Column('product_group', sa.String(24), nullable=False),
        sa.Column('external_order_id', sa.String(64)),
        sa.Column('release_method', sa.String(32)),
        sa.Column('status', sa.String(24), nullable=False, server_default='draft'),
        sa.Column('idempotency_key', sa.String(128)),
        sa.Column('errors', JSONB, nullable=False, server_default='[]'),
        sa.Column('expected_completion_at', sa.DateTime(timezone=True)),
        _created(),
        _updated(),
        sa.UniqueConstraint('crpt_client_id', 'external_order_id', name='uq_km_order_client_external'),
        sa.UniqueConstraint('idempotency_key', name='uq_km_order_idempotency'),
    )
    op.create_index('ix_marking_km_orders_company', 'marking_km_orders', ['company_id'])
    op.create_index('ix_marking_km_orders_client', 'marking_km_orders', ['crpt_client_id'])
    op.create_index('ix_marking_km_orders_app', 'marking_km_orders', ['application_id'])
    op.create_index('ix_marking_km_orders_extid', 'marking_km_orders', ['external_order_id'])

    op.create_table(
        'marking_km_order_items',
        _uuid_pk(),
        sa.Column('order_id', UUID, sa.ForeignKey('marking_km_orders.id', ondelete='CASCADE'), nullable=False),
        sa.Column('gtin', sa.String(14), nullable=False),
        sa.Column('template_id', sa.String(32)),
        sa.Column('cis_type', sa.String(32)),
        sa.Column('serial_number_type', sa.String(32)),
        sa.Column('ordered_quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('ready_quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('received_quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_block_id', sa.String(64)),
        sa.Column('status', sa.String(24), nullable=False, server_default='draft'),
        _created(),
        _updated(),
    )
    op.create_index('ix_marking_km_items_order', 'marking_km_order_items', ['order_id'])

    op.create_table(
        'marking_km_code_batches',
        _uuid_pk(),
        _company(),
        sa.Column('order_item_id', UUID, sa.ForeignKey('marking_km_order_items.id', ondelete='CASCADE'), nullable=False),
        sa.Column('gtin', sa.String(14), nullable=False),
        sa.Column('external_order_id', sa.String(64)),
        sa.Column('block_id', sa.String(64)),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(24), nullable=False, server_default='received'),
        sa.Column('storage_path', sa.String(512)),
        sa.Column('encrypted_file_hash', sa.String(64)),
        _created(),
    )
    op.create_index('ix_marking_batches_company', 'marking_km_code_batches', ['company_id'])
    op.create_index('ix_marking_batches_item', 'marking_km_code_batches', ['order_item_id'])

    op.create_table(
        'marking_km_code_hashes',
        _uuid_pk(),
        _company(),
        sa.Column('crpt_client_id', UUID, sa.ForeignKey('marking_crpt_clients.id', ondelete='CASCADE'), nullable=False),
        sa.Column('batch_id', UUID, sa.ForeignKey('marking_km_code_batches.id', ondelete='SET NULL')),
        sa.Column('km_hash', sa.String(64), nullable=False),
        _created(),
        sa.UniqueConstraint('crpt_client_id', 'km_hash', name='uq_km_hash_client'),
    )
    op.create_index('ix_marking_km_hashes_company', 'marking_km_code_hashes', ['company_id'])
    op.create_index('ix_marking_km_hashes_client', 'marking_km_code_hashes', ['crpt_client_id'])
    op.create_index('ix_marking_km_hashes_hash', 'marking_km_code_hashes', ['km_hash'])

    op.create_table(
        'marking_application_reports',
        _uuid_pk(),
        _company(),
        sa.Column('crpt_client_id', UUID, sa.ForeignKey('marking_crpt_clients.id', ondelete='CASCADE'), nullable=False),
        sa.Column('application_id', UUID, sa.ForeignKey('marking_applications.id', ondelete='SET NULL')),
        sa.Column('product_group', sa.String(24), nullable=False),
        sa.Column('mode', sa.String(16), nullable=False, server_default='auto'),
        sa.Column('status', sa.String(24), nullable=False, server_default='draft'),
        sa.Column('external_report_id', sa.String(64)),
        sa.Column('total_rows', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('summary', JSONB, nullable=False, server_default='{}'),
        sa.Column('source_file_path', sa.String(512)),
        _created(),
        _updated(),
    )
    op.create_index('ix_marking_reports_company', 'marking_application_reports', ['company_id'])
    op.create_index('ix_marking_reports_client', 'marking_application_reports', ['crpt_client_id'])
    op.create_index('ix_marking_reports_app', 'marking_application_reports', ['application_id'])

    op.create_table(
        'marking_circulation_documents',
        _uuid_pk(),
        _company(),
        sa.Column('crpt_client_id', UUID, sa.ForeignKey('marking_crpt_clients.id', ondelete='CASCADE'), nullable=False),
        sa.Column('application_id', UUID, sa.ForeignKey('marking_applications.id', ondelete='SET NULL')),
        sa.Column('product_group', sa.String(24), nullable=False),
        sa.Column('workflow_type', sa.String(32), nullable=False),
        sa.Column('document_type', sa.String(64)),
        sa.Column('status', sa.String(24), nullable=False, server_default='draft'),
        sa.Column('external_document_id', sa.String(64)),
        sa.Column('idempotency_key', sa.String(128)),
        sa.Column('payload', JSONB, nullable=False, server_default='{}'),
        sa.Column('validation', JSONB, nullable=False, server_default='{}'),
        sa.Column('receipt', JSONB, nullable=False, server_default='{}'),
        _created(),
        _updated(),
        sa.UniqueConstraint('crpt_client_id', 'external_document_id', name='uq_circ_doc_client_external'),
        sa.UniqueConstraint('idempotency_key', name='uq_circ_doc_idempotency'),
    )
    op.create_index('ix_marking_circ_company', 'marking_circulation_documents', ['company_id'])
    op.create_index('ix_marking_circ_client', 'marking_circulation_documents', ['crpt_client_id'])
    op.create_index('ix_marking_circ_app', 'marking_circulation_documents', ['application_id'])
    op.create_index('ix_marking_circ_extid', 'marking_circulation_documents', ['external_document_id'])

    op.create_table(
        'marking_circulation_document_items',
        _uuid_pk(),
        sa.Column('document_id', UUID, sa.ForeignKey('marking_circulation_documents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('gtin', sa.String(14)),
        sa.Column('km_masked', sa.String(64)),
        sa.Column('km_hash', sa.String(64)),
        sa.Column('status', sa.String(24), nullable=False, server_default='draft'),
        sa.Column('errors', JSONB, nullable=False, server_default='[]'),
        _created(),
    )
    op.create_index('ix_marking_circ_items_doc', 'marking_circulation_document_items', ['document_id'])
    op.create_index('ix_marking_circ_items_hash', 'marking_circulation_document_items', ['km_hash'])

    op.create_table(
        'marking_sign_jobs',
        _uuid_pk(),
        _company(),
        sa.Column('crpt_client_id', UUID, sa.ForeignKey('marking_crpt_clients.id', ondelete='SET NULL')),
        sa.Column('signer_agent_id', UUID, sa.ForeignKey('marking_signer_agents.id', ondelete='SET NULL')),
        sa.Column('idempotency_key', sa.String(128)),
        sa.Column('sign_type', sa.String(16), nullable=False, server_default='detached'),
        sa.Column('payload_base64', sa.Text()),
        sa.Column('payload_sha256', sa.String(64), nullable=False),
        sa.Column('certificate_thumbprint', sa.String(80)),
        sa.Column('client_inn', sa.String(12)),
        sa.Column('operation', sa.String(128)),
        sa.Column('status', sa.String(16), nullable=False, server_default='pending'),
        sa.Column('signature_base64', sa.Text()),
        sa.Column('error', sa.Text()),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('claimed_at', sa.DateTime(timezone=True)),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        _created(),
        _updated(),
    )
    op.create_index('ix_marking_sign_jobs_company', 'marking_sign_jobs', ['company_id'])
    op.create_index('ix_marking_sign_jobs_client', 'marking_sign_jobs', ['crpt_client_id'])
    op.create_index('ix_marking_sign_jobs_agent', 'marking_sign_jobs', ['signer_agent_id'])
    op.create_index('ix_marking_sign_jobs_status', 'marking_sign_jobs', ['status'])

    op.create_table(
        'marking_operation_jobs',
        _uuid_pk(),
        _company(),
        sa.Column('crpt_client_id', UUID, sa.ForeignKey('marking_crpt_clients.id', ondelete='SET NULL')),
        sa.Column('application_id', UUID, sa.ForeignKey('marking_applications.id', ondelete='SET NULL')),
        sa.Column('kind', sa.String(48), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, server_default='pending'),
        sa.Column('progress', JSONB, nullable=False, server_default='{}'),
        sa.Column('result', JSONB, nullable=False, server_default='{}'),
        sa.Column('error', sa.Text()),
        sa.Column('correlation_id', sa.String(64)),
        sa.Column('idempotency_key', sa.String(128)),
        sa.Column('created_by', UUID, sa.ForeignKey('users.id', ondelete='SET NULL')),
        _created(),
        _updated(),
        sa.UniqueConstraint('idempotency_key', name='uq_marking_op_idempotency'),
    )
    op.create_index('ix_marking_op_jobs_company', 'marking_operation_jobs', ['company_id'])
    op.create_index('ix_marking_op_jobs_client', 'marking_operation_jobs', ['crpt_client_id'])
    op.create_index('ix_marking_op_jobs_status', 'marking_operation_jobs', ['status'])

    op.create_table(
        'marking_operation_logs',
        _uuid_pk(),
        _company(),
        sa.Column('crpt_client_id', UUID, sa.ForeignKey('marking_crpt_clients.id', ondelete='SET NULL')),
        sa.Column('application_id', UUID, sa.ForeignKey('marking_applications.id', ondelete='SET NULL')),
        sa.Column('user_id', UUID, sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('client_inn', sa.String(12)),
        sa.Column('operation', sa.String(64), nullable=False),
        sa.Column('object_type', sa.String(48)),
        sa.Column('object_id', sa.String(64)),
        sa.Column('rows_or_km_count', sa.Integer()),
        sa.Column('result', sa.String(24), nullable=False, server_default='ok'),
        sa.Column('external_id', sa.String(64)),
        sa.Column('correlation_id', sa.String(64)),
        sa.Column('error_message', sa.Text()),
        _created(),
    )
    op.create_index('ix_marking_op_logs_company', 'marking_operation_logs', ['company_id'])
    op.create_index('ix_marking_op_logs_client', 'marking_operation_logs', ['crpt_client_id'])
    op.create_index('ix_marking_op_logs_operation', 'marking_operation_logs', ['operation'])


def downgrade() -> None:
    for table in [
        'marking_operation_logs',
        'marking_operation_jobs',
        'marking_sign_jobs',
        'marking_circulation_document_items',
        'marking_circulation_documents',
        'marking_application_reports',
        'marking_km_code_hashes',
        'marking_km_code_batches',
        'marking_km_order_items',
        'marking_km_orders',
        'marking_nk_feed_items',
        'marking_nk_feeds',
        'marking_product_cards',
        'marking_applications',
        'marking_mchd_access_profiles',
        'marking_client_connection_checks',
        'marking_crpt_clients',
        'marking_signer_agents',
    ]:
        op.drop_table(table)
