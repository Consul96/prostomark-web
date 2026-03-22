import re
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud.company import create_company, get_company_by_slug
from app.crud.subscription import get_active_company_subscription, get_plan_by_code
from app.crud.user import create_user, get_user_by_email
from app.models.enums import SubscriptionStatus, UserRole
from app.models.subscription import CompanySubscription
from app.models.token import RefreshToken
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest
from app.security.password import hash_password, verify_and_update_password
from app.security.tokens import (
    TokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_token,
)


def _slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r'[^a-z0-9]+', '-', value)
    return value.strip('-') or 'company'


def _unique_company_slug(db: Session, preferred: str) -> str:
    base = _slugify(preferred)
    candidate = base
    i = 1
    while get_company_by_slug(db, candidate) is not None:
        i += 1
        candidate = f'{base}-{i}'
    return candidate


def authenticate_user(db: Session, payload: LoginRequest) -> User:
    user = get_user_by_email(db, payload.email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid email or password')

    is_valid, new_hash = verify_and_update_password(payload.password, user.password_hash)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid email or password')

    if new_hash is not None:
        user.password_hash = new_hash
        db.flush()

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User is inactive')
    return user


def register(db: Session, payload: RegisterRequest) -> User:
    if get_user_by_email(db, payload.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Email is already registered')

    company_slug = _unique_company_slug(db, payload.company_slug or payload.company_name)
    company = create_company(db, name=payload.company_name, slug=company_slug)

    user = User(
        company_id=company.id,
        email=payload.email,
        password_hash=hash_password(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        role=UserRole.COMPANY_ADMIN,
        is_active=True,
        is_email_verified=False,
    )
    create_user(db, user)

    if get_active_company_subscription(db, company.id) is None:
        trial_plan = get_plan_by_code(db, 'trial')
        if trial_plan is not None:
            db.add(
                CompanySubscription(
                    company_id=company.id,
                    plan_id=trial_plan.id,
                    status=SubscriptionStatus.TRIAL,
                )
            )

    return user


def issue_tokens(db: Session, user: User) -> tuple[str, str]:
    access_token = create_access_token(str(user.id), str(user.role), str(user.company_id))
    refresh_token, expires_at, _ = create_refresh_token(str(user.id), str(user.role), str(user.company_id))

    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_token(refresh_token),
            expires_at=expires_at,
        )
    )

    return access_token, refresh_token


def rotate_refresh_token(db: Session, refresh_token: str) -> tuple[User, str, str]:
    try:
        payload = decode_token(refresh_token)
    except TokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token') from exc

    if payload.get('type') != 'refresh':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token type')

    token_hash = hash_token(refresh_token)
    token_row = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).one_or_none()
    if token_row is None or token_row.revoked_at is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Refresh token revoked')

    if token_row.expires_at < datetime.now(UTC):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Refresh token expired')

    user = db.get(User, token_row.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User unavailable')

    token_row.revoked_at = datetime.now(UTC)
    access_token, new_refresh_token = issue_tokens(db, user)
    return user, access_token, new_refresh_token


def revoke_refresh_token(db: Session, refresh_token: str) -> None:
    token_hash = hash_token(refresh_token)
    token_row = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).one_or_none()
    if token_row and token_row.revoked_at is None:
        token_row.revoked_at = datetime.now(UTC)
