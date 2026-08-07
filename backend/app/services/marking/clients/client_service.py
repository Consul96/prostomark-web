"""Сервис клиентов Честного знака (CrptClient). Строгая изоляция по company_id."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import ConnectionStatus
from app.models.marking import ClientConnectionCheck, CrptClient
from app.services.marking.auth.mchd_service import evaluate_mchd_status
from app.services.marking.errors import MarkingError


def _scoped_query(company_id: uuid.UUID):
    return select(CrptClient).where(CrptClient.company_id == company_id)


def list_clients(db: Session, company_id: uuid.UUID) -> list[CrptClient]:
    return list(db.execute(_scoped_query(company_id).order_by(CrptClient.created_at.desc())).scalars())


def get_client(db: Session, company_id: uuid.UUID, client_id: uuid.UUID) -> CrptClient:
    client = db.execute(
        _scoped_query(company_id).where(CrptClient.id == client_id)
    ).scalar_one_or_none()
    if client is None:
        raise MarkingError('Клиент не найден', code='MARKING_CLIENT_NOT_FOUND', http_status=404)
    return client


def create_client(db: Session, company_id: uuid.UUID, data: dict) -> CrptClient:
    existing = db.execute(
        _scoped_query(company_id).where(
            CrptClient.inn == data['inn'],
            CrptClient.environment == data.get('environment', 'sandbox'),
        )
    ).scalar_one_or_none()
    if existing is not None:
        raise MarkingError(
            'Клиент с таким ИНН уже существует в этом окружении',
            code='MARKING_CLIENT_DUPLICATE',
            http_status=409,
        )
    client = CrptClient(company_id=company_id, **data)
    client.mchd_status = evaluate_mchd_status(client)
    db.add(client)
    db.flush()
    return client


def update_client(db: Session, company_id: uuid.UUID, client_id: uuid.UUID, data: dict) -> CrptClient:
    client = get_client(db, company_id, client_id)
    for k, v in data.items():
        setattr(client, k, v)
    client.mchd_status = evaluate_mchd_status(client)
    db.flush()
    return client


def deactivate_client(db: Session, company_id: uuid.UUID, client_id: uuid.UUID) -> CrptClient:
    client = get_client(db, company_id, client_id)
    client.is_active = False
    db.flush()
    return client


def record_connection_check(
    db: Session, client: CrptClient, *, kind: str, status: str, detail: str | None = None, correlation_id: str | None = None
) -> ClientConnectionCheck:
    check = ClientConnectionCheck(
        company_id=client.company_id,
        crpt_client_id=client.id,
        kind=kind,
        status=status,
        detail=detail,
        correlation_id=correlation_id,
    )
    db.add(check)
    client.last_connection_check_at = datetime.now(UTC)
    db.flush()
    return check


def check_connections(db: Session, client: CrptClient) -> dict:
    """Безопасная проверка конфигурации подключения (без юридически значимых вызовов).

    Реальные сетевые проверки True API/СУЗ подключаются в Phase 2/3; здесь —
    детерминированная оценка готовности конфигурации + статус МЧД.
    """
    mchd = evaluate_mchd_status(client)
    client.mchd_status = mchd

    def cfg_status(ok: bool) -> str:
        return ConnectionStatus.OK.value if ok else ConnectionStatus.NEEDS_SETUP.value

    true_api_ready = bool(client.signer_agent_id and client.product_groups)
    suz_ready = bool(client.oms_id and client.oms_connection and client.signer_agent_id)

    client.true_api_status = cfg_status(true_api_ready)
    client.suz_status = cfg_status(suz_ready)

    record_connection_check(db, client, kind='mchd', status=mchd)
    record_connection_check(db, client, kind='true_api', status=client.true_api_status)
    record_connection_check(db, client, kind='suz', status=client.suz_status)
    db.flush()
    return {
        'mchd_status': mchd,
        'true_api_status': client.true_api_status,
        'suz_status': client.suz_status,
    }
