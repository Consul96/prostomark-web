from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.schemas.auth import AuthResponse, LoginRequest, LogoutRequest, RefreshRequest, RegisterRequest, TokenPair
from app.schemas.user import UserRead
from app.services.audit_service import log_audit
from app.services.auth_service import (
    authenticate_user,
    issue_tokens,
    register,
    revoke_refresh_token,
    rotate_refresh_token,
)

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/register', response_model=AuthResponse)
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    user = register(db, payload)
    access_token, refresh_token = issue_tokens(db, user)

    log_audit(
        db,
        company_id=user.company_id,
        user_id=user.id,
        action='auth.register',
        entity_type='user',
        entity_id=str(user.id),
        meta_json={'email': user.email},
    )
    db.commit()
    db.refresh(user)

    return AuthResponse(tokens=TokenPair(access_token=access_token, refresh_token=refresh_token), user=UserRead.model_validate(user))


@router.post('/login', response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    user = authenticate_user(db, payload)
    access_token, refresh_token = issue_tokens(db, user)

    log_audit(
        db,
        company_id=user.company_id,
        user_id=user.id,
        action='auth.login',
        entity_type='user',
        entity_id=str(user.id),
    )
    db.commit()

    return AuthResponse(tokens=TokenPair(access_token=access_token, refresh_token=refresh_token), user=UserRead.model_validate(user))


@router.post('/refresh', response_model=AuthResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> AuthResponse:
    user, access_token, refresh_token = rotate_refresh_token(db, payload.refresh_token)
    db.commit()
    return AuthResponse(tokens=TokenPair(access_token=access_token, refresh_token=refresh_token), user=UserRead.model_validate(user))


@router.post('/logout')
def logout(payload: LogoutRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    revoke_refresh_token(db, payload.refresh_token)
    db.commit()
    return {'message': 'Logged out'}


@router.get('/me', response_model=UserRead)
def me(current_user=Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)
