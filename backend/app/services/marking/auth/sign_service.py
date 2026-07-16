"""Сервис подписи через выносной Sign Agent (CryptoPro CSP).

Закрытый ключ не хранится на VPS. Backend ставит SignJob, агент забирает её по
HTTPS (исходящее подключение), подписывает точные байты и возвращает CMS Base64.

Здесь — только серверная часть постановки/ожидания задачи и mock-подписант для
тестов и sandbox. Реальная подпись выполняется агентом (см. каталог sign-agent/).
"""

from __future__ import annotations

import base64
import hashlib
import time
from abc import ABC, abstractmethod
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.config import settings
from app.models.enums import SignJobStatus
from app.models.marking import SignJob
from app.services.marking.errors import PayloadHashMismatchError, SignAgentUnavailableError


def payload_sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


class Signer(ABC):
    @abstractmethod
    def sign(self, payload: bytes, *, detached: bool, thumbprint: str | None) -> str:
        """Возвращает CMS-подпись в Base64."""


class MockSigner(Signer):
    """Детерминированный подписант для тестов/sandbox (НЕ криптографическая подпись)."""

    def sign(self, payload: bytes, *, detached: bool, thumbprint: str | None) -> str:
        marker = b'MOCK-DETACHED:' if detached else b'MOCK-ATTACHED:'
        digest = hashlib.sha256(payload).digest()
        body = marker + digest if detached else marker + payload
        return base64.b64encode(body).decode('ascii')


def create_sign_job(
    db: Session,
    *,
    company_id,
    payload: bytes,
    detached: bool,
    client_inn: str | None,
    operation: str,
    certificate_thumbprint: str | None,
    crpt_client_id=None,
    signer_agent_id=None,
    idempotency_key: str | None = None,
) -> SignJob:
    job = SignJob(
        company_id=company_id,
        crpt_client_id=crpt_client_id,
        signer_agent_id=signer_agent_id,
        idempotency_key=idempotency_key,
        sign_type=('detached' if detached else 'attached'),
        payload_base64=base64.b64encode(payload).decode('ascii'),
        payload_sha256=payload_sha256(payload),
        certificate_thumbprint=certificate_thumbprint,
        client_inn=client_inn,
        operation=operation,
        status=SignJobStatus.PENDING.value,
        expires_at=datetime.now(UTC) + timedelta(seconds=settings.sign_job_ttl_seconds),
    )
    db.add(job)
    db.flush()
    return job


def complete_sign_job(db: Session, job: SignJob, *, signature_base64: str, payload_sha256_from_agent: str) -> SignJob:
    """Агент вернул подпись. Проверяем совпадение хеша payload перед сохранением."""
    if payload_sha256_from_agent != job.payload_sha256:
        raise PayloadHashMismatchError(details={'job_id': str(job.id)})
    job.signature_base64 = signature_base64
    job.status = SignJobStatus.COMPLETED.value
    job.completed_at = datetime.now(UTC)
    db.flush()
    return job


def sign_with_mock(db: Session, job: SignJob) -> SignJob:
    """Синхронная подпись mock-подписантом (sandbox/dry-run/тесты)."""
    payload = base64.b64decode(job.payload_base64 or '')
    signature = MockSigner().sign(payload, detached=(job.sign_type == 'detached'), thumbprint=job.certificate_thumbprint)
    return complete_sign_job(
        db, job, signature_base64=signature, payload_sha256_from_agent=payload_sha256(payload)
    )


def wait_for_signature(db: Session, job: SignJob, *, timeout: float | None = None) -> str:
    """Ожидает завершения SignJob агентом. Возвращает подпись Base64.

    В dry-run/sandbox можно сразу подписать mock-подписантом — вызывающий код
    решает это по окружению. Здесь — только ожидание уже поставленной задачи.
    """
    deadline = time.time() + (timeout or settings.sign_job_ttl_seconds)
    while time.time() < deadline:
        db.refresh(job)
        if job.status == SignJobStatus.COMPLETED.value and job.signature_base64:
            return job.signature_base64
        if job.status in {SignJobStatus.FAILED.value, SignJobStatus.EXPIRED.value}:
            raise SignAgentUnavailableError(details={'job_id': str(job.id), 'status': job.status})
        time.sleep(1.0)
    raise SignAgentUnavailableError(details={'job_id': str(job.id), 'reason': 'timeout'})
