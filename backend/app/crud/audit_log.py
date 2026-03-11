from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def create_log(db: Session, log: AuditLog) -> AuditLog:
    db.add(log)
    db.flush()
    return log


def list_logs(db: Session, *, company_id: str | None = None, limit: int = 50, offset: int = 0) -> list[AuditLog]:
    stmt = select(AuditLog).order_by(AuditLog.created_at.desc())
    if company_id:
        stmt = stmt.where(AuditLog.company_id == company_id)
    stmt = stmt.limit(limit).offset(offset)
    return list(db.execute(stmt).scalars().all())
