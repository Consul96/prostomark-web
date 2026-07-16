"""Модели модуля «Честный знак» (marking).

Мультиклиентская модель: все сущности привязаны к company_id (организация —
пользователь платформы ProstoMark) и, где применимо, к crpt_client_id (клиент
Честного знака, от имени которого Cargo-Trans работает по МЧД).

ВАЖНО про КМ: полные коды маркировки НИКОГДА не хранятся построчно в PostgreSQL.
В БД хранятся только метаданные партии (KmCodeBatch): GTIN, orderId, blockId,
количество, статус, путь к зашифрованному файлу, его хеш. Сами коды лежат в
зашифрованном файловом хранилище (см. services/marking/storage/encrypted_storage.py).
Для антидублей — HMAC (km_hash) в отдельной таблице без открытого КМ.
"""

import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPKMixin


def _company_fk() -> Mapped[uuid.UUID]:
    return mapped_column(UUID(as_uuid=True), ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True)


class UpdatedAtMixin:
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class SignerAgent(Base, UUIDPKMixin, TimestampMixin, UpdatedAtMixin):
    """Выносной агент подписи (Windows + CryptoPro CSP). Закрытые ключи на VPS не хранятся."""

    __tablename__ = 'marking_signer_agents'

    company_id: Mapped[uuid.UUID] = _company_fk()
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # HMAC-SHA256 от API-ключа агента (сам ключ не хранится).
    api_key_hash: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    certificate_thumbprint: Mapped[str | None] = mapped_column(String(80), nullable=True)
    certificate_subject: Mapped[str | None] = mapped_column(String(512), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    version: Mapped[str | None] = mapped_column(String(64), nullable=True)


class CrptClient(Base, UUIDPKMixin, TimestampMixin, UpdatedAtMixin):
    """Клиент Честного знака (организация, от имени которой работаем по МЧД)."""

    __tablename__ = 'marking_crpt_clients'
    __table_args__ = (
        UniqueConstraint('company_id', 'inn', 'environment', name='uq_crpt_client_company_inn_env'),
    )

    company_id: Mapped[uuid.UUID] = _company_fk()
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    inn: Mapped[str] = mapped_column(String(12), nullable=False, index=True)
    environment: Mapped[str] = mapped_column(String(16), nullable=False, default='sandbox')
    # Список кодов товарных групп (ProductGroupCode).
    product_groups: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    oms_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    oms_connection: Mapped[str | None] = mapped_column(String(128), nullable=True)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default='Europe/Moscow')

    signer_agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('marking_signer_agents.id', ondelete='SET NULL'), nullable=True
    )
    signer_certificate_thumbprint: Mapped[str | None] = mapped_column(String(80), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    true_api_status: Mapped[str] = mapped_column(String(24), nullable=False, default='unknown')
    suz_status: Mapped[str] = mapped_column(String(24), nullable=False, default='unknown')
    mchd_status: Mapped[str] = mapped_column(String(24), nullable=False, default='unknown')
    mchd_number: Mapped[str | None] = mapped_column(String(128), nullable=True)
    mchd_valid_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    mchd_valid_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    last_connection_check_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    settings: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    signer_agent = relationship('SignerAgent')
    connection_checks = relationship(
        'ClientConnectionCheck', back_populates='client', cascade='all, delete-orphan'
    )


class ClientConnectionCheck(Base, UUIDPKMixin, TimestampMixin):
    """Журнал проверок подключения клиента (МЧД / True API / СУЗ)."""

    __tablename__ = 'marking_client_connection_checks'

    company_id: Mapped[uuid.UUID] = _company_fk()
    crpt_client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('marking_crpt_clients.id', ondelete='CASCADE'), nullable=False, index=True
    )
    kind: Mapped[str] = mapped_column(String(24), nullable=False)  # mchd | true_api | suz | sign_agent
    status: Mapped[str] = mapped_column(String(24), nullable=False)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    correlation_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    client = relationship('CrptClient', back_populates='connection_checks')


class MchdAccessProfile(Base, UUIDPKMixin, TimestampMixin, UpdatedAtMixin):
    """Профиль доступа по МЧД: связка подписант ↔ клиент ↔ товарная группа."""

    __tablename__ = 'marking_mchd_access_profiles'

    company_id: Mapped[uuid.UUID] = _company_fk()
    crpt_client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('marking_crpt_clients.id', ondelete='CASCADE'), nullable=False, index=True
    )
    signer_agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('marking_signer_agents.id', ondelete='SET NULL'), nullable=True
    )
    signer_certificate_thumbprint: Mapped[str | None] = mapped_column(String(80), nullable=True)
    signer_inn: Mapped[str | None] = mapped_column(String(12), nullable=True)
    mchd_number: Mapped[str | None] = mapped_column(String(128), nullable=True)
    mchd_valid_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    mchd_valid_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default='unknown')
    product_groups: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)


class MarkingApplication(Base, UUIDPKMixin, TimestampMixin, UpdatedAtMixin):
    """Центральная сущность — заявка на маркировку, объединяющая все этапы."""

    __tablename__ = 'marking_applications'

    company_id: Mapped[uuid.UUID] = _company_fk()
    crpt_client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('marking_crpt_clients.id', ondelete='RESTRICT'), nullable=False, index=True
    )
    external_application_number: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    product_group: Mapped[str] = mapped_column(String(24), nullable=False)
    workflow_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    release_method: Mapped[str | None] = mapped_column(String(32), nullable=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default='draft')
    progress: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True
    )
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True
    )
    meta: Mapped[dict] = mapped_column('metadata', JSONB, nullable=False, default=dict)


class MarkingProductCard(Base, UUIDPKMixin, TimestampMixin, UpdatedAtMixin):
    """Карточка товара Национального каталога (не заменяет базовый Product)."""

    __tablename__ = 'marking_product_cards'

    company_id: Mapped[uuid.UUID] = _company_fk()
    crpt_client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('marking_crpt_clients.id', ondelete='CASCADE'), nullable=False, index=True
    )
    application_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('marking_applications.id', ondelete='SET NULL'), nullable=True, index=True
    )
    # Опциональная связь с базовым товаром платформы.
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('products.id', ondelete='SET NULL'), nullable=True
    )
    product_group: Mapped[str] = mapped_column(String(24), nullable=False)
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    article: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    brand: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tnved: Mapped[str | None] = mapped_column(String(16), nullable=True)
    # Динамические атрибуты товарной группы (пол, возраст, состав, цвет, размер и т.д.).
    attributes: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    gtin: Mapped[str | None] = mapped_column(String(14), nullable=True, index=True)
    good_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    nk_status: Mapped[str] = mapped_column(String(24), nullable=False, default='draft')
    errors: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)


class NkFeed(Base, UUIDPKMixin, TimestampMixin, UpdatedAtMixin):
    """Фид карточек в Национальный каталог."""

    __tablename__ = 'marking_nk_feeds'

    company_id: Mapped[uuid.UUID] = _company_fk()
    crpt_client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('marking_crpt_clients.id', ondelete='CASCADE'), nullable=False, index=True
    )
    application_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('marking_applications.id', ondelete='SET NULL'), nullable=True
    )
    external_feed_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default='draft')
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    result: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    items = relationship('NkFeedItem', back_populates='feed', cascade='all, delete-orphan')


class NkFeedItem(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = 'marking_nk_feed_items'

    feed_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('marking_nk_feeds.id', ondelete='CASCADE'), nullable=False, index=True
    )
    product_card_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('marking_product_cards.id', ondelete='SET NULL'), nullable=True
    )
    gtin: Mapped[str | None] = mapped_column(String(14), nullable=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default='draft')
    errors: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    feed = relationship('NkFeed', back_populates='items')


class KmOrder(Base, UUIDPKMixin, TimestampMixin, UpdatedAtMixin):
    """Заказ на эмиссию кодов маркировки (СУЗ)."""

    __tablename__ = 'marking_km_orders'
    __table_args__ = (
        UniqueConstraint('crpt_client_id', 'external_order_id', name='uq_km_order_client_external'),
    )

    company_id: Mapped[uuid.UUID] = _company_fk()
    crpt_client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('marking_crpt_clients.id', ondelete='CASCADE'), nullable=False, index=True
    )
    application_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('marking_applications.id', ondelete='SET NULL'), nullable=True, index=True
    )
    product_group: Mapped[str] = mapped_column(String(24), nullable=False)
    external_order_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    release_method: Mapped[str | None] = mapped_column(String(32), nullable=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default='draft')
    # Идемпотентность создания заказа во внешней системе.
    idempotency_key: Mapped[str | None] = mapped_column(String(128), nullable=True, unique=True)
    errors: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    expected_completion_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    items = relationship('KmOrderItem', back_populates='order', cascade='all, delete-orphan')


class KmOrderItem(Base, UUIDPKMixin, TimestampMixin, UpdatedAtMixin):
    __tablename__ = 'marking_km_order_items'

    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('marking_km_orders.id', ondelete='CASCADE'), nullable=False, index=True
    )
    gtin: Mapped[str] = mapped_column(String(14), nullable=False)
    template_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    cis_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    serial_number_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    ordered_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ready_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    received_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_block_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default='draft')

    order = relationship('KmOrder', back_populates='items')
    batches = relationship('KmCodeBatch', back_populates='order_item', cascade='all, delete-orphan')


class KmCodeBatch(Base, UUIDPKMixin, TimestampMixin):
    """Метаданные партии полученных КМ. Сами коды — в зашифрованном файле."""

    __tablename__ = 'marking_km_code_batches'

    company_id: Mapped[uuid.UUID] = _company_fk()
    order_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('marking_km_order_items.id', ondelete='CASCADE'), nullable=False, index=True
    )
    gtin: Mapped[str] = mapped_column(String(14), nullable=False)
    external_order_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    block_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default='received')
    # Путь к зашифрованному файлу с полными КМ (относительно marking_storage_path).
    storage_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    # SHA-256 зашифрованного файла (проверка целостности).
    encrypted_file_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)

    order_item = relationship('KmOrderItem', back_populates='batches')


class KmCodeHash(Base, UUIDPKMixin):
    """HMAC-SHA256 полного КМ — для поиска дублей без хранения открытого кода."""

    __tablename__ = 'marking_km_code_hashes'
    __table_args__ = (
        UniqueConstraint('crpt_client_id', 'km_hash', name='uq_km_hash_client'),
    )

    company_id: Mapped[uuid.UUID] = _company_fk()
    crpt_client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('marking_crpt_clients.id', ondelete='CASCADE'), nullable=False, index=True
    )
    batch_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('marking_km_code_batches.id', ondelete='SET NULL'), nullable=True
    )
    km_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class ApplicationReport(Base, UUIDPKMixin, TimestampMixin, UpdatedAtMixin):
    """Отчёт/контроль нанесения КМ."""

    __tablename__ = 'marking_application_reports'

    company_id: Mapped[uuid.UUID] = _company_fk()
    crpt_client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('marking_crpt_clients.id', ondelete='CASCADE'), nullable=False, index=True
    )
    application_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('marking_applications.id', ondelete='SET NULL'), nullable=True, index=True
    )
    product_group: Mapped[str] = mapped_column(String(24), nullable=False)
    # auto (контроль через True API) | manual (ручной отчёт в СУЗ)
    mode: Mapped[str] = mapped_column(String(16), nullable=False, default='auto')
    status: Mapped[str] = mapped_column(String(24), nullable=False, default='draft')
    external_report_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    total_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    summary: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    # Путь к исходному загруженному файлу (хранится для аудита).
    source_file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)


class CirculationDocument(Base, UUIDPKMixin, TimestampMixin, UpdatedAtMixin):
    """Документ ввода в оборот."""

    __tablename__ = 'marking_circulation_documents'
    __table_args__ = (
        UniqueConstraint('crpt_client_id', 'external_document_id', name='uq_circ_doc_client_external'),
    )

    company_id: Mapped[uuid.UUID] = _company_fk()
    crpt_client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('marking_crpt_clients.id', ondelete='CASCADE'), nullable=False, index=True
    )
    application_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('marking_applications.id', ondelete='SET NULL'), nullable=True, index=True
    )
    product_group: Mapped[str] = mapped_column(String(24), nullable=False)
    workflow_type: Mapped[str] = mapped_column(String(32), nullable=False)
    document_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default='draft')
    external_document_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(128), nullable=True, unique=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    validation: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    receipt: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    items = relationship('CirculationDocumentItem', back_populates='document', cascade='all, delete-orphan')


class CirculationDocumentItem(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = 'marking_circulation_document_items'

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('marking_circulation_documents.id', ondelete='CASCADE'), nullable=False, index=True
    )
    gtin: Mapped[str | None] = mapped_column(String(14), nullable=True)
    # Маскированное представление КМ для UI (полный код тут НЕ хранится).
    km_masked: Mapped[str | None] = mapped_column(String(64), nullable=True)
    km_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default='draft')
    errors: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    document = relationship('CirculationDocument', back_populates='items')


class SignJob(Base, UUIDPKMixin, TimestampMixin, UpdatedAtMixin):
    """Задача подписи для Sign Agent. Payload и подпись маскируются в логах."""

    __tablename__ = 'marking_sign_jobs'

    company_id: Mapped[uuid.UUID] = _company_fk()
    crpt_client_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('marking_crpt_clients.id', ondelete='SET NULL'), nullable=True, index=True
    )
    signer_agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('marking_signer_agents.id', ondelete='SET NULL'), nullable=True, index=True
    )
    idempotency_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    sign_type: Mapped[str] = mapped_column(String(16), nullable=False, default='detached')
    payload_base64: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    certificate_thumbprint: Mapped[str | None] = mapped_column(String(80), nullable=True)
    client_inn: Mapped[str | None] = mapped_column(String(12), nullable=True)
    operation: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default='pending', index=True)
    signature_base64: Mapped[str | None] = mapped_column(Text, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    claimed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class MarkingOperationJob(Base, UUIDPKMixin, TimestampMixin, UpdatedAtMixin):
    """Фоновая операция (Excel-парсинг, polling, выгрузка КМ, отправка и т.д.)."""

    __tablename__ = 'marking_operation_jobs'
    __table_args__ = (
        UniqueConstraint('idempotency_key', name='uq_marking_op_idempotency'),
    )

    company_id: Mapped[uuid.UUID] = _company_fk()
    crpt_client_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('marking_crpt_clients.id', ondelete='SET NULL'), nullable=True, index=True
    )
    application_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('marking_applications.id', ondelete='SET NULL'), nullable=True
    )
    kind: Mapped[str] = mapped_column(String(48), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default='pending', index=True)
    progress: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    result: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    correlation_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True
    )


class MarkingOperationLog(Base, UUIDPKMixin):
    """История/аудит операций модуля. Токены, ключи, полные КМ сюда не пишутся."""

    __tablename__ = 'marking_operation_logs'

    company_id: Mapped[uuid.UUID] = _company_fk()
    crpt_client_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('marking_crpt_clients.id', ondelete='SET NULL'), nullable=True, index=True
    )
    application_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('marking_applications.id', ondelete='SET NULL'), nullable=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True
    )
    client_inn: Mapped[str | None] = mapped_column(String(12), nullable=True)
    operation: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    object_type: Mapped[str | None] = mapped_column(String(48), nullable=True)
    object_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    rows_or_km_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    result: Mapped[str] = mapped_column(String(24), nullable=False, default='ok')
    external_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    correlation_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
