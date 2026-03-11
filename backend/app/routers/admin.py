from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.crud.audit_log import list_logs
from app.crud.company import list_companies
from app.crud.subscription import list_subscriptions
from app.crud.user import create_user, get_user_by_email, list_users
from app.db import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.admin import AdminUserCreate, AuditLogOut, CompanyOut, CompanySubscriptionOut, UserRead
from app.security.password import hash_password
from app.security.permissions import require_roles
from app.services.audit_service import log_audit

router = APIRouter(prefix='/admin', tags=['admin'])


@router.get('/users', response_model=list[UserRead])
def admin_users(
    company_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.SUPERADMIN)),
) -> list[UserRead]:
    return [UserRead.model_validate(item) for item in list_users(db, company_id=company_id, limit=limit, offset=offset)]


@router.post('/users', response_model=UserRead, status_code=status.HTTP_201_CREATED)
def admin_users_create(
    payload: AdminUserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPERADMIN)),
) -> UserRead:
    if get_user_by_email(db, payload.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Email already exists')

    row = User(
        company_id=payload.company_id,
        email=payload.email,
        password_hash=hash_password(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        role=payload.role,
        is_active=payload.is_active,
        is_email_verified=payload.is_email_verified,
    )
    create_user(db, row)

    log_audit(
        db,
        company_id=row.company_id,
        user_id=current_user.id,
        action='admin.users.create',
        entity_type='user',
        entity_id=str(row.id),
    )
    db.commit()
    db.refresh(row)
    return UserRead.model_validate(row)


@router.get('/companies', response_model=list[CompanyOut])
def admin_companies(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.SUPERADMIN)),
) -> list[CompanyOut]:
    return [CompanyOut.model_validate(item) for item in list_companies(db, limit=limit, offset=offset)]


@router.get('/subscriptions', response_model=list[CompanySubscriptionOut])
def admin_subscriptions(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.SUPERADMIN)),
) -> list[CompanySubscriptionOut]:
    return [CompanySubscriptionOut.model_validate(item) for item in list_subscriptions(db, limit=limit, offset=offset)]


@router.get('/logs', response_model=list[AuditLogOut])
def admin_logs(
    company_id: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=300),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.SUPERADMIN)),
) -> list[AuditLogOut]:
    return [AuditLogOut.model_validate(item) for item in list_logs(db, company_id=company_id, limit=limit, offset=offset)]
