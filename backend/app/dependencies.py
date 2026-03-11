import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.security.tokens import TokenError, decode_token

bearer_scheme = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except TokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials') from exc

    if payload.get('type') != 'access':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid access token')

    user_id = payload.get('sub')
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token payload')

    user = db.get(User, uuid.UUID(user_id))
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found or inactive')
    return user


def ensure_company_access(target_company_id: uuid.UUID, user: User) -> None:
    if str(user.role) == 'superadmin':
        return
    if user.company_id != target_company_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Cross-tenant access denied')
