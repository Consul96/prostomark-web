"""TrueApiTokenManager — получение и кеширование единого токена True API.

Документированный поток (True API, /auth/key + /auth/simpleSignIn):
  1. GET  /auth/key            -> пара {uuid, data}
  2. Подписать `data` УКЭП (присоединённая CMS, Base64) через Sign Agent
  3. POST /auth/simpleSignIn   {uuid, data: <подпись Base64>, inn: <ИНН клиента>}
     -> {token | uuidToken, ...}
  4. Использовать: Authorization: Bearer <token>

challenge UUID никогда не переиспользуется. Ключ кеша:
  true-api:{environment}:{signer_id}:{client_inn}

См. docs/marking/crpt-api-mapping.md (True API auth).
"""

from __future__ import annotations

import time
from collections.abc import Callable

from app.config import settings
from app.services.marking.auth import token_cache as tc
from app.services.marking.errors import ExternalAuthError
from app.services.marking.http_client import MarkingHttpClient

# Подписант: принимает строку `data`, возвращает CMS Base64. Инъекция ради тестов.
SignCallback = Callable[[str], str]

# Токен True API в формате UUID/JWT; срок задаём консервативно (10 часов),
# если ответ не содержит явного времени истечения.
_DEFAULT_TTL_SECONDS = 10 * 3600


class TrueApiTokenManager:
    def __init__(self, *, base_url: str | None = None) -> None:
        self.base_url = base_url or settings.crpt_true_api_base_url

    def _client(self) -> MarkingHttpClient:
        return MarkingHttpClient(self.base_url)

    def _authenticate(self, *, signer_id: str, client_inn: str, sign: SignCallback) -> tc.CachedToken:
        client = self._client()
        # 1. challenge
        key_resp = client.request('GET', '/auth/key').json()
        challenge_uuid = key_resp['uuid']
        data = key_resp['data']
        # 2. подпись
        signature = sign(data)
        # 3. simpleSignIn
        signin = client.request(
            'POST',
            '/auth/simpleSignIn',
            json={'uuid': challenge_uuid, 'data': signature, 'inn': client_inn},
        ).json()
        token = signin.get('token') or signin.get('uuidToken')
        if not token:
            raise ExternalAuthError('Внешняя система не вернула токен', details={'keys': list(signin.keys())})
        expires_at = time.time() + _DEFAULT_TTL_SECONDS
        return tc.CachedToken(token=token, expires_at=expires_at)

    def get_token(
        self,
        *,
        environment: str,
        signer_id: str,
        client_inn: str,
        sign: SignCallback,
        force_refresh: bool = False,
    ) -> str:
        key = tc.true_api_cache_key(environment, signer_id, client_inn)
        if not force_refresh:
            cached = tc.read_token(key)
            if cached and cached.is_fresh():
                return cached.token
        with tc.RedisLock(key):
            cached = tc.read_token(key)
            if cached and cached.is_fresh() and not force_refresh:
                return cached.token
            fresh = self._authenticate(signer_id=signer_id, client_inn=client_inn, sign=sign)
            tc.write_token(key, fresh.token, fresh.expires_at)
            return fresh.token

    def invalidate(self, *, environment: str, signer_id: str, client_inn: str) -> None:
        tc.invalidate(tc.true_api_cache_key(environment, signer_id, client_inn))
