"""Кеш токенов и распределённые блокировки на Redis.

Ключи кеша (по спецификации):
  * True API:  true-api:{environment}:{signer_id}:{client_inn}
  * СУЗ:       suz:{environment}:{signer_id}:{client_inn}:{oms_connection}

Токены НЕ попадают во frontend, audit log и обычные application logs.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass

import redis

from app.config import settings

_redis: redis.Redis | None = None


def get_redis() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    return _redis


def true_api_cache_key(environment: str, signer_id: str, client_inn: str) -> str:
    return f'true-api:{environment}:{signer_id}:{client_inn}'


def suz_cache_key(environment: str, signer_id: str, client_inn: str, oms_connection: str) -> str:
    return f'suz:{environment}:{signer_id}:{client_inn}:{oms_connection}'


@dataclass
class CachedToken:
    token: str
    expires_at: float  # unix ts

    def is_fresh(self, skew: float = 60.0) -> bool:
        # Упреждающее обновление: считаем истёкшим за `skew` секунд до конца.
        return time.time() < (self.expires_at - skew)


def read_token(key: str) -> CachedToken | None:
    raw = get_redis().get(key)
    if not raw:
        return None
    data = json.loads(raw)
    return CachedToken(token=data['token'], expires_at=float(data['expires_at']))


def write_token(key: str, token: str, expires_at: float) -> None:
    ttl = max(1, int(expires_at - time.time()))
    get_redis().set(key, json.dumps({'token': token, 'expires_at': expires_at}), ex=ttl)


def invalidate(key: str) -> None:
    get_redis().delete(key)


class RedisLock:
    """Простая блокировка для сериализации обновления токена (один активный
    СУЗ-токен на omsConnection; предотвращает гонку обновления)."""

    def __init__(self, key: str, ttl: int = 30) -> None:
        self.key = f'lock:{key}'
        self.ttl = ttl
        self._token = str(time.time())

    def __enter__(self) -> RedisLock:
        deadline = time.time() + self.ttl
        while time.time() < deadline:
            if get_redis().set(self.key, self._token, nx=True, ex=self.ttl):
                return self
            time.sleep(0.1)
        # Не удалось взять блокировку — продолжаем без неё (best-effort).
        return self

    def __exit__(self, *exc) -> None:
        try:
            if get_redis().get(self.key) == self._token:
                get_redis().delete(self.key)
        except Exception:  # noqa: BLE001
            pass
