from uuid import UUID

from sqlalchemy.orm import Session

from app.crud.audit_log import create_log
from app.models.audit_log import AuditLog


def log_audit(
    db: Session,
    *,
    company_id: UUID | None,
    user_id: UUID | None,
    action: str,
    entity_type: str,
    entity_id: str | None,
    meta_json: dict | None = None,
) -> AuditLog:
    audit = AuditLog(
        company_id=company_id,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        meta_json=meta_json or {},
    )
    return create_log(db, audit)
