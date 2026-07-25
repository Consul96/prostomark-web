"""Pydantic-схемы модуля «Честный знак» (marking)."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase

# --------------------------- Клиенты ---------------------------


class CrptClientBase(BaseModel):
    name: str
    inn: str = Field(min_length=10, max_length=12)
    environment: str = 'sandbox'
    product_groups: list[str] = Field(default_factory=list)
    oms_id: str | None = None
    oms_connection: str | None = None
    timezone: str = 'Europe/Moscow'
    signer_agent_id: UUID | None = None
    signer_certificate_thumbprint: str | None = None
    mchd_number: str | None = None
    mchd_valid_from: date | None = None
    mchd_valid_until: date | None = None
    settings: dict = Field(default_factory=dict)


class CrptClientCreate(CrptClientBase):
    pass


class CrptClientUpdate(BaseModel):
    name: str | None = None
    environment: str | None = None
    product_groups: list[str] | None = None
    oms_id: str | None = None
    oms_connection: str | None = None
    timezone: str | None = None
    signer_agent_id: UUID | None = None
    signer_certificate_thumbprint: str | None = None
    is_active: bool | None = None
    mchd_number: str | None = None
    mchd_valid_from: date | None = None
    mchd_valid_until: date | None = None
    settings: dict | None = None


class CrptClientOut(ORMBase):
    id: UUID
    company_id: UUID
    name: str
    inn: str
    environment: str
    product_groups: list
    oms_id: str | None
    oms_connection: str | None
    timezone: str
    signer_agent_id: UUID | None
    signer_certificate_thumbprint: str | None
    is_active: bool
    true_api_status: str
    suz_status: str
    mchd_status: str
    mchd_number: str | None
    mchd_valid_from: date | None
    mchd_valid_until: date | None
    last_connection_check_at: datetime | None
    settings: dict
    created_at: datetime
    updated_at: datetime


class ConnectionCheckResult(BaseModel):
    mchd_status: str
    true_api_status: str
    suz_status: str


# --------------------------- Заявки ---------------------------


class MarkingApplicationCreate(BaseModel):
    crpt_client_id: UUID
    title: str
    product_group: str
    external_application_number: str | None = None
    workflow_type: str | None = None
    release_method: str | None = None
    assigned_to: UUID | None = None
    metadata: dict = Field(default_factory=dict)


class MarkingApplicationUpdate(BaseModel):
    title: str | None = None
    status: str | None = None
    workflow_type: str | None = None
    release_method: str | None = None
    assigned_to: UUID | None = None
    metadata: dict | None = None


class MarkingApplicationOut(ORMBase):
    id: UUID
    company_id: UUID
    crpt_client_id: UUID
    external_application_number: str | None
    title: str
    product_group: str
    workflow_type: str | None
    release_method: str | None
    status: str
    progress: dict
    created_by: UUID | None
    assigned_to: UUID | None
    created_at: datetime
    updated_at: datetime


# --------------------------- Sign Agent ---------------------------


class SignerAgentCreate(BaseModel):
    name: str
    certificate_thumbprint: str | None = None
    certificate_subject: str | None = None


class SignerAgentOut(ORMBase):
    id: UUID
    company_id: UUID
    name: str
    certificate_thumbprint: str | None
    certificate_subject: str | None
    is_active: bool
    last_heartbeat_at: datetime | None
    version: str | None
    created_at: datetime


class SignerAgentCreated(SignerAgentOut):
    # API-ключ показывается ОДИН раз при создании (далее хранится только hash).
    api_key: str


class SignJobOut(ORMBase):
    id: UUID
    sign_type: str
    payload_sha256: str
    certificate_thumbprint: str | None
    client_inn: str | None
    operation: str | None
    status: str
    expires_at: datetime
    created_at: datetime


class SignAgentClaimOut(BaseModel):
    job_id: UUID | None
    sign_type: str | None = None
    payload_base64: str | None = None
    payload_sha256: str | None = None
    certificate_thumbprint: str | None = None
    client_inn: str | None = None
    operation: str | None = None
    expires_at: datetime | None = None


class SignAgentResult(BaseModel):
    job_id: UUID
    signature_base64: str
    payload_sha256: str


class SignAgentError(BaseModel):
    job_id: UUID
    error: str


# --------------------------- Jobs ---------------------------


class OperationJobOut(ORMBase):
    id: UUID
    kind: str
    status: str
    progress: dict
    result: dict
    error: str | None
    correlation_id: str | None
    created_at: datetime
    updated_at: datetime


# --------------------------- Dashboard / история ---------------------------


class DashboardOut(BaseModel):
    active_applications: int
    cards_with_errors: int
    gtin_pending_publication: int
    km_orders_processing: int
    km_ready_to_receive: int
    application_report_mismatches: int
    circulation_pending_signature: int
    circulation_rejected: int
    mchd_expiring: int
    sign_agents_unavailable: int
    attention: list[dict] = Field(default_factory=list)


class OperationLogOut(ORMBase):
    id: UUID
    crpt_client_id: UUID | None
    application_id: UUID | None
    user_id: UUID | None
    client_inn: str | None
    operation: str
    object_type: str | None
    object_id: str | None
    rows_or_km_count: int | None
    result: str
    external_id: str | None
    correlation_id: str | None
    error_message: str | None
    created_at: datetime
