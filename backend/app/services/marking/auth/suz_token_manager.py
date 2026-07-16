"""SuzTokenManager — получение и кеширование clientToken СУЗ.

Документированный поток (API СУЗ 3.0):
  1. GET  /auth/key                       -> {uuid, data}
  2. Подписать `data` сертификатом сотрудника (CMS Base64)
  3. Авторизация по omsConnection + ИНН клиента
  4. Получить отдельный clientToken
  5. clientToken передаётся в заголовке `clientToken` запросов СУЗ.

Ключ кеша:
  suz:{environment}:{signer_id}:{client_inn}:{oms_connection}

Особенности: один активный СУЗ-токен на omsConnection (Redis-lock сериализует
обновление); новый токен может инвалидировать предыдущий; при 401 — одна
повторная авторизация. True API token и СУЗ clientToken НЕ смешиваются.

⚠️ Точный URL авторизации СУЗ (шаг 3) не выделен отдельным разделом в
предоставленной версии PDF — см. crpt-api-mapping.md, помечен как требующий
подтверждения. Метод структурно готов, endpoint параметризован.
"""

from __future__ import annotations

import time
from collections.abc import Callable

from app.config import settings
from app.services.marking.auth import token_cache as tc
from app.services.marking.errors import ExternalAuthError
from app.services.marking.http_client import MarkingHttpClient

SignCallback = Callable[[str], str]

_DEFAULT_TTL_SECONDS = 10 * 3600


class SuzTokenManager:
    def __init__(self, *, base_url: str | None = None, auth_path: str = '/api/v3/auth/simpleSignIn') -> None:
        self.base_url = base_url or settings.crpt_suz_base_url
        # ⚠️ auth_path требует подтверждения документацией СУЗ.
        self.auth_path = auth_path

    def _client(self) -> MarkingHttpClient:
        return MarkingHttpClient(self.base_url)

    def _authenticate(
        self, *, oms_connection: str, client_inn: str, sign: SignCallback
    ) -> tc.CachedToken:
        client = self._client()
        key_resp = client.request('GET', '/api/v3/auth/key').json()
        challenge_uuid = key_resp['uuid']
        data = key_resp['data']
        signature = sign(data)
        signin = client.request(
            'POST',
            self.auth_path,
            json={
                'uuid': challenge_uuid,
                'data': signature,
                'inn': client_inn,
                'connectionId': oms_connection,
            },
        ).json()
        token = signin.get('clientToken') or signin.get('token')
        if not token:
            raise ExternalAuthError('СУЗ не вернул clientToken', details={'keys': list(signin.keys())})
        return tc.CachedToken(token=token, expires_at=time.time() + _DEFAULT_TTL_SECONDS)

    def get_token(
        self,
        *,
        environment: str,
        signer_id: str,
        client_inn: str,
        oms_connection: str,
        sign: SignCallback,
        force_refresh: bool = False,
    ) -> str:
        key = tc.suz_cache_key(environment, signer_id, client_inn, oms_connection)
        if not force_refresh:
            cached = tc.read_token(key)
            if cached and cached.is_fresh():
                return cached.token
        # Один активный токен на omsConnection — сериализуем обновление.
        with tc.RedisLock(key):
            cached = tc.read_token(key)
            if cached and cached.is_fresh() and not force_refresh:
                return cached.token
            fresh = self._authenticate(oms_connection=oms_connection, client_inn=client_inn, sign=sign)
            tc.write_token(key, fresh.token, fresh.expires_at)
            return fresh.token

    def invalidate(self, *, environment: str, signer_id: str, client_inn: str, oms_connection: str) -> None:
        tc.invalidate(tc.suz_cache_key(environment, signer_id, client_inn, oms_connection))
