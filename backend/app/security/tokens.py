import hashlib
import uuid
from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

from app.config import settings


class TokenError(Exception):
    pass


def _build_payload(user_id: str, role: str, company_id: str, token_type: str, expires_delta: timedelta, jti: str | None = None) -> dict:
    now = datetime.now(UTC)
    exp = now + expires_delta
    return {
        'sub': user_id,
        'role': role,
        'company_id': company_id,
        'type': token_type,
        'jti': jti or str(uuid.uuid4()),
        'iat': int(now.timestamp()),
        'exp': int(exp.timestamp()),
    }


def create_access_token(user_id: str, role: str, company_id: str) -> str:
    payload = _build_payload(
        user_id=user_id,
        role=role,
        company_id=company_id,
        token_type='access',
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: str, role: str, company_id: str) -> tuple[str, datetime, str]:
    expires_delta = timedelta(days=settings.refresh_token_expire_days)
    payload = _build_payload(
        user_id=user_id,
        role=role,
        company_id=company_id,
        token_type='refresh',
        expires_delta=expires_delta,
    )
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    expires_at = datetime.fromtimestamp(payload['exp'], tz=UTC)
    return token, expires_at, payload['jti']


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise TokenError('Invalid token') from exc


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode('utf-8')).hexdigest()
