"""Роутер модуля «Честный знак» (marking). Базовый префикс: /api/v1/marking.

Группы: /dashboard, /clients, /applications, /sign-agent, /jobs, /history.
Все выборки строго изолированы по current_user.company_id. Роли:
  * company_admin — управление клиентами, агентами, операциями;
  * manager       — создание и выполнение операций;
  * user          — просмотр (без управления подключением);
  * superadmin    — полный доступ (обрабатывается в require_roles).
"""

from __future__ import annotations

import secrets
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models.enums import (
    CirculationDocumentStatus,
    KmOrderStatus,
    MarkingApplicationStatus,
    MchdStatus,
    ProductCardStatus,
    SignJobStatus,
    UserRole,
)
from app.models.marking import (
    CirculationDocument,
    CrptClient,
    KmOrder,
    MarkingApplication,
    MarkingOperationJob,
    MarkingOperationLog,
    MarkingProductCard,
    SignerAgent,
    SignJob,
)
from app.models.user import User
from app.schemas.marking import (
    ConnectionCheckResult,
    CrptClientCreate,
    CrptClientOut,
    CrptClientUpdate,
    DashboardOut,
    MarkingApplicationCreate,
    MarkingApplicationOut,
    MarkingApplicationUpdate,
    OperationJobOut,
    OperationLogOut,
    SignAgentClaimOut,
    SignAgentError,
    SignAgentResult,
    SignerAgentCreate,
    SignerAgentCreated,
    SignerAgentOut,
    SignJobOut,
)
from app.security.permissions import require_roles
from app.security.tokens import hash_token
from app.services.marking.auth import sign_service
from app.services.marking.clients import client_service, connection_service
from app.services.marking.jobs import job_service

router = APIRouter(prefix='/marking', tags=['marking'])

_MANAGE = require_roles(UserRole.COMPANY_ADMIN, UserRole.MANAGER)
_ADMIN = require_roles(UserRole.COMPANY_ADMIN)
_VIEW = get_current_user  # любой аутентифицированный пользователь компании


# =========================================================================
# Dashboard
# =========================================================================


@router.get('/dashboard', response_model=DashboardOut)
def dashboard(db: Session = Depends(get_db), user: User = Depends(_VIEW)) -> DashboardOut:
    cid = user.company_id

    def count(stmt) -> int:
        return int(db.execute(stmt).scalar() or 0)

    base_app = select(func.count(MarkingApplication.id)).where(MarkingApplication.company_id == cid)
    active_apps = count(base_app.where(MarkingApplication.status == MarkingApplicationStatus.IN_PROGRESS.value))

    cards_err = count(
        select(func.count(MarkingProductCard.id)).where(
            MarkingProductCard.company_id == cid, MarkingProductCard.nk_status == ProductCardStatus.ERROR.value
        )
    )
    gtin_pending = count(
        select(func.count(MarkingProductCard.id)).where(
            MarkingProductCard.company_id == cid,
            MarkingProductCard.nk_status.in_(
                [ProductCardStatus.GTIN_ASSIGNED.value, ProductCardStatus.MODERATION.value]
            ),
        )
    )
    orders_proc = count(
        select(func.count(KmOrder.id)).where(
            KmOrder.company_id == cid,
            KmOrder.status.in_([KmOrderStatus.SENT.value, KmOrderStatus.PENDING.value]),
        )
    )
    km_ready = count(
        select(func.count(KmOrder.id)).where(
            KmOrder.company_id == cid, KmOrder.status == KmOrderStatus.READY.value
        )
    )
    circ_pending = count(
        select(func.count(CirculationDocument.id)).where(
            CirculationDocument.company_id == cid,
            CirculationDocument.status == CirculationDocumentStatus.WAITING_FOR_SIGNATURE.value,
        )
    )
    circ_rejected = count(
        select(func.count(CirculationDocument.id)).where(
            CirculationDocument.company_id == cid,
            CirculationDocument.status == CirculationDocumentStatus.REJECTED.value,
        )
    )
    mchd_expiring = count(
        select(func.count(CrptClient.id)).where(
            CrptClient.company_id == cid, CrptClient.mchd_status == MchdStatus.EXPIRED.value
        )
    )
    agents_down = count(
        select(func.count(SignerAgent.id)).where(
            SignerAgent.company_id == cid, SignerAgent.is_active.is_(False)
        )
    )

    attention: list[dict] = []
    if mchd_expiring:
        attention.append({'type': 'mchd_expired', 'count': mchd_expiring, 'message': 'Есть клиенты с истёкшей МЧД'})
    if cards_err:
        attention.append({'type': 'cards_error', 'count': cards_err, 'message': 'Карточки с ошибками'})
    if circ_rejected:
        attention.append({'type': 'circulation_rejected', 'count': circ_rejected, 'message': 'Отклонённые документы ввода'})

    return DashboardOut(
        active_applications=active_apps,
        cards_with_errors=cards_err,
        gtin_pending_publication=gtin_pending,
        km_orders_processing=orders_proc,
        km_ready_to_receive=km_ready,
        application_report_mismatches=0,
        circulation_pending_signature=circ_pending,
        circulation_rejected=circ_rejected,
        mchd_expiring=mchd_expiring,
        sign_agents_unavailable=agents_down,
        attention=attention,
    )


# =========================================================================
# Клиенты
# =========================================================================


@router.get('/clients', response_model=list[CrptClientOut])
def clients_index(db: Session = Depends(get_db), user: User = Depends(_VIEW)) -> list[CrptClientOut]:
    return [CrptClientOut.model_validate(c) for c in client_service.list_clients(db, user.company_id)]


@router.post('/clients', response_model=CrptClientOut, status_code=status.HTTP_201_CREATED)
def clients_create(payload: CrptClientCreate, db: Session = Depends(get_db), user: User = Depends(_MANAGE)) -> CrptClientOut:
    client = client_service.create_client(db, user.company_id, payload.model_dump())
    _log(db, user, operation='client.create', object_type='crpt_client', object_id=str(client.id), client=client)
    db.commit()
    db.refresh(client)
    return CrptClientOut.model_validate(client)


@router.get('/clients/{client_id}', response_model=CrptClientOut)
def clients_get(client_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(_VIEW)) -> CrptClientOut:
    return CrptClientOut.model_validate(client_service.get_client(db, user.company_id, client_id))


@router.patch('/clients/{client_id}', response_model=CrptClientOut)
def clients_update(
    client_id: uuid.UUID, payload: CrptClientUpdate, db: Session = Depends(get_db), user: User = Depends(_MANAGE)
) -> CrptClientOut:
    data = {k: v for k, v in payload.model_dump().items() if v is not None}
    client = client_service.update_client(db, user.company_id, client_id, data)
    db.commit()
    db.refresh(client)
    return CrptClientOut.model_validate(client)


@router.post('/clients/{client_id}/deactivate', response_model=CrptClientOut)
def clients_deactivate(client_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(_ADMIN)) -> CrptClientOut:
    client = client_service.deactivate_client(db, user.company_id, client_id)
    db.commit()
    db.refresh(client)
    return CrptClientOut.model_validate(client)


@router.post('/clients/{client_id}/check-connection', response_model=ConnectionCheckResult)
def clients_check(client_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(_MANAGE)) -> ConnectionCheckResult:
    client = client_service.get_client(db, user.company_id, client_id)
    result = client_service.check_connections(db, client)
    db.commit()
    return ConnectionCheckResult(**result)


@router.post('/clients/{client_id}/sandbox-connection-test')
def clients_sandbox_connection_test(
    client_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(_MANAGE)
) -> dict:
    """Реальная проверка аутентификации в True API и СУЗ (sandbox) через МЧД + Sign Agent.

    Статус `ok` только при реально полученном токене; заполненность конфигурации
    сама по себе `ok` не даёт. Юридически значимые операции не выполняются.
    """
    client = client_service.get_client(db, user.company_id, client_id)
    return connection_service.run_connection_test(db, client)


# =========================================================================
# Заявки
# =========================================================================


@router.get('/applications', response_model=list[MarkingApplicationOut])
def applications_index(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(_VIEW),
) -> list[MarkingApplicationOut]:
    rows = db.execute(
        select(MarkingApplication)
        .where(MarkingApplication.company_id == user.company_id)
        .order_by(MarkingApplication.created_at.desc())
        .limit(limit)
        .offset(offset)
    ).scalars()
    return [MarkingApplicationOut.model_validate(r) for r in rows]


@router.post('/applications', response_model=MarkingApplicationOut, status_code=status.HTTP_201_CREATED)
def applications_create(
    payload: MarkingApplicationCreate, db: Session = Depends(get_db), user: User = Depends(_MANAGE)
) -> MarkingApplicationOut:
    # Проверяем принадлежность клиента этой компании (защита от подмены UUID).
    client_service.get_client(db, user.company_id, payload.crpt_client_id)
    data = payload.model_dump()
    meta = data.pop('metadata')
    app_row = MarkingApplication(
        company_id=user.company_id,
        created_by=user.id,
        status=MarkingApplicationStatus.DRAFT.value,
        meta=meta,
        **data,
    )
    db.add(app_row)
    db.flush()
    _log(db, user, operation='application.create', object_type='marking_application', object_id=str(app_row.id))
    db.commit()
    db.refresh(app_row)
    return MarkingApplicationOut.model_validate(app_row)


def _get_application(db: Session, user: User, application_id: uuid.UUID) -> MarkingApplication:
    row = db.execute(
        select(MarkingApplication).where(
            MarkingApplication.company_id == user.company_id, MarkingApplication.id == application_id
        )
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail='Заявка не найдена')
    return row


@router.get('/applications/{application_id}', response_model=MarkingApplicationOut)
def applications_get(application_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(_VIEW)) -> MarkingApplicationOut:
    return MarkingApplicationOut.model_validate(_get_application(db, user, application_id))


@router.patch('/applications/{application_id}', response_model=MarkingApplicationOut)
def applications_update(
    application_id: uuid.UUID, payload: MarkingApplicationUpdate, db: Session = Depends(get_db), user: User = Depends(_MANAGE)
) -> MarkingApplicationOut:
    row = _get_application(db, user, application_id)
    data = {k: v for k, v in payload.model_dump().items() if v is not None}
    meta = data.pop('metadata', None)
    if meta is not None:
        row.meta = meta
    for k, v in data.items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return MarkingApplicationOut.model_validate(row)


# =========================================================================
# Sign Agent — управление (пользователи)
# =========================================================================


@router.get('/sign-agent/agents', response_model=list[SignerAgentOut])
def agents_index(db: Session = Depends(get_db), user: User = Depends(_VIEW)) -> list[SignerAgentOut]:
    rows = db.execute(select(SignerAgent).where(SignerAgent.company_id == user.company_id)).scalars()
    return [SignerAgentOut.model_validate(r) for r in rows]


@router.post('/sign-agent/agents', response_model=SignerAgentCreated, status_code=status.HTTP_201_CREATED)
def agents_create(payload: SignerAgentCreate, db: Session = Depends(get_db), user: User = Depends(_ADMIN)) -> SignerAgentCreated:
    api_key = secrets.token_urlsafe(32)
    agent = SignerAgent(
        company_id=user.company_id,
        name=payload.name,
        api_key_hash=hash_token(api_key),
        certificate_thumbprint=payload.certificate_thumbprint,
        certificate_subject=payload.certificate_subject,
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    # api_key показывается один раз; в БД хранится только его hash.
    base = SignerAgentOut.model_validate(agent).model_dump()
    return SignerAgentCreated(**base, api_key=api_key)


# --- внутренний протокол агента (аутентификация по API-ключу, не по JWT) ---


def get_agent(
    x_agent_api_key: str = Header(..., alias='X-Agent-Api-Key'),
    db: Session = Depends(get_db),
) -> SignerAgent:
    agent = db.execute(
        select(SignerAgent).where(SignerAgent.api_key_hash == hash_token(x_agent_api_key))
    ).scalar_one_or_none()
    if agent is None or not agent.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid agent key')
    return agent


@router.post('/sign-agent/heartbeat')
def agent_heartbeat(agent: SignerAgent = Depends(get_agent), db: Session = Depends(get_db)) -> dict:
    agent.last_heartbeat_at = datetime.now(UTC)
    db.commit()
    return {'status': 'ok'}


@router.get('/sign-agent/next-job', response_model=SignAgentClaimOut)
def agent_next_job(agent: SignerAgent = Depends(get_agent), db: Session = Depends(get_db)) -> SignAgentClaimOut:
    now = datetime.now(UTC)
    job = db.execute(
        select(SignJob)
        .where(
            SignJob.company_id == agent.company_id,
            SignJob.status == SignJobStatus.PENDING.value,
            SignJob.expires_at > now,
        )
        .order_by(SignJob.created_at.asc())
        .limit(1)
        .with_for_update(skip_locked=True)
    ).scalar_one_or_none()
    if job is None:
        return SignAgentClaimOut(job_id=None)
    job.status = SignJobStatus.CLAIMED.value
    job.signer_agent_id = agent.id
    job.claimed_at = now
    db.commit()
    db.refresh(job)
    return SignAgentClaimOut(
        job_id=job.id,
        sign_type=job.sign_type,
        payload_base64=job.payload_base64,
        payload_sha256=job.payload_sha256,
        certificate_thumbprint=job.certificate_thumbprint,
        client_inn=job.client_inn,
        operation=job.operation,
        expires_at=job.expires_at,
    )


@router.post('/sign-agent/result')
def agent_result(payload: SignAgentResult, agent: SignerAgent = Depends(get_agent), db: Session = Depends(get_db)) -> dict:
    job = db.get(SignJob, payload.job_id)
    if job is None or job.company_id != agent.company_id:
        raise HTTPException(status_code=404, detail='Job not found')
    # Просроченную задачу подписывать нельзя.
    if job.status != SignJobStatus.COMPLETED.value and job.expires_at < datetime.now(UTC):
        job.status = SignJobStatus.EXPIRED.value
        db.commit()
        raise HTTPException(status_code=409, detail='Sign job expired')
    # Терминальное состояние — повторный результат не принимаем (идемпотентность/защита).
    if job.status in {SignJobStatus.COMPLETED.value, SignJobStatus.FAILED.value, SignJobStatus.EXPIRED.value}:
        if job.status == SignJobStatus.COMPLETED.value and payload.payload_sha256 == job.payload_sha256:
            # Дубль того же результата — отвечаем идемпотентно, ничего не меняем.
            return {'status': 'ok', 'idempotent': True}
        raise HTTPException(status_code=409, detail=f'Sign job already {job.status}')
    sign_service.complete_sign_job(
        db, job, signature_base64=payload.signature_base64, payload_sha256_from_agent=payload.payload_sha256
    )
    db.commit()
    return {'status': 'ok'}


@router.post('/sign-agent/error')
def agent_error(payload: SignAgentError, agent: SignerAgent = Depends(get_agent), db: Session = Depends(get_db)) -> dict:
    job = db.get(SignJob, payload.job_id)
    if job is None or job.company_id != agent.company_id:
        raise HTTPException(status_code=404, detail='Job not found')
    job.status = SignJobStatus.FAILED.value
    job.error = payload.error[:2000]
    db.commit()
    return {'status': 'ok'}


@router.get('/sign-agent/jobs', response_model=list[SignJobOut])
def sign_jobs_index(db: Session = Depends(get_db), user: User = Depends(_VIEW)) -> list[SignJobOut]:
    rows = db.execute(
        select(SignJob).where(SignJob.company_id == user.company_id).order_by(SignJob.created_at.desc()).limit(100)
    ).scalars()
    return [SignJobOut.model_validate(r) for r in rows]


# =========================================================================
# Jobs
# =========================================================================


@router.get('/jobs/{job_id}', response_model=OperationJobOut)
def jobs_get(job_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(_VIEW)) -> OperationJobOut:
    return OperationJobOut.model_validate(job_service.get_job(db, user.company_id, job_id))


@router.get('/jobs', response_model=list[OperationJobOut])
def jobs_index(db: Session = Depends(get_db), user: User = Depends(_VIEW)) -> list[OperationJobOut]:
    rows = db.execute(
        select(MarkingOperationJob)
        .where(MarkingOperationJob.company_id == user.company_id)
        .order_by(MarkingOperationJob.created_at.desc())
        .limit(100)
    ).scalars()
    return [OperationJobOut.model_validate(r) for r in rows]


# =========================================================================
# История / аудит
# =========================================================================


@router.get('/history', response_model=list[OperationLogOut])
def history_index(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    operation: str | None = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(_VIEW),
) -> list[OperationLogOut]:
    stmt = select(MarkingOperationLog).where(MarkingOperationLog.company_id == user.company_id)
    if operation:
        stmt = stmt.where(MarkingOperationLog.operation == operation)
    stmt = stmt.order_by(MarkingOperationLog.created_at.desc()).limit(limit).offset(offset)
    return [OperationLogOut.model_validate(r) for r in db.execute(stmt).scalars()]


# --------------------------- helpers ---------------------------


def _log(
    db: Session,
    user: User,
    *,
    operation: str,
    object_type: str | None = None,
    object_id: str | None = None,
    client: CrptClient | None = None,
    rows_or_km_count: int | None = None,
    result: str = 'ok',
    correlation_id: str | None = None,
) -> None:
    db.add(
        MarkingOperationLog(
            company_id=user.company_id,
            crpt_client_id=client.id if client else None,
            user_id=user.id,
            client_inn=client.inn if client else None,
            operation=operation,
            object_type=object_type,
            object_id=object_id,
            rows_or_km_count=rows_or_km_count,
            result=result,
            correlation_id=correlation_id,
        )
    )
