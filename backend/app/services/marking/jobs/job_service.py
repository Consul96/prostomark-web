"""Сервис фоновых операций (MarkingOperationJob). Прогресс и статусы."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import OperationJobStatus
from app.models.marking import MarkingOperationJob
from app.services.marking.errors import MarkingError


def create_job(
    db: Session,
    *,
    company_id: uuid.UUID,
    kind: str,
    crpt_client_id: uuid.UUID | None = None,
    application_id: uuid.UUID | None = None,
    created_by: uuid.UUID | None = None,
    idempotency_key: str | None = None,
    correlation_id: str | None = None,
) -> MarkingOperationJob:
    if idempotency_key:
        existing = db.execute(
            select(MarkingOperationJob).where(
                MarkingOperationJob.company_id == company_id,
                MarkingOperationJob.idempotency_key == idempotency_key,
            )
        ).scalar_one_or_none()
        if existing is not None:
            return existing
    job = MarkingOperationJob(
        company_id=company_id,
        kind=kind,
        crpt_client_id=crpt_client_id,
        application_id=application_id,
        created_by=created_by,
        idempotency_key=idempotency_key,
        correlation_id=correlation_id,
        status=OperationJobStatus.PENDING.value,
    )
    db.add(job)
    db.flush()
    return job


def get_job(db: Session, company_id: uuid.UUID, job_id: uuid.UUID) -> MarkingOperationJob:
    job = db.execute(
        select(MarkingOperationJob).where(
            MarkingOperationJob.company_id == company_id, MarkingOperationJob.id == job_id
        )
    ).scalar_one_or_none()
    if job is None:
        raise MarkingError('Задача не найдена', code='MARKING_JOB_NOT_FOUND', http_status=404)
    return job


def set_status(db: Session, job: MarkingOperationJob, status: str, *, progress: dict | None = None, result: dict | None = None, error: str | None = None) -> MarkingOperationJob:
    job.status = status
    if progress is not None:
        job.progress = progress
    if result is not None:
        job.result = result
    if error is not None:
        job.error = error
    db.flush()
    return job
