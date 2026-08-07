"""Единый HTTP-клиент для внешних систем ГИС МТ (True API / СУЗ / НК).

Особенности:
  * timeout из настроек;
  * correlation ID на каждый запрос;
  * безопасное логирование (токены/КМ маскируются, тела с секретами не пишутся);
  * типизированные ошибки (ExternalApiError / ExternalAuthError / RateLimitedError);
  * обработка 401 (инвалидация токена — на стороне вызывающего) и 429;
  * retry ТОЛЬКО для идемпотентных операций (GET) с ограниченным числом попыток;
  * поддержка idempotency-key для create-операций.

Юридически значимые POST не повторяются вслепую после неоднозначного network
timeout — это ответственность вызывающего кода (см. submission_service).
"""

from __future__ import annotations

import logging
import uuid

import httpx

from app.config import settings
from app.services.marking.errors import ExternalApiError, ExternalAuthError, RateLimitedError

logger = logging.getLogger('marking.http')

_SAFE_RETRY_METHODS = {'GET', 'HEAD'}
_MAX_SAFE_RETRIES = 2


def new_correlation_id() -> str:
    return uuid.uuid4().hex


def _mask_headers(headers: dict) -> dict:
    masked = {}
    for k, v in headers.items():
        if k.lower() in {'authorization', 'clienttoken', 'x-api-key'}:
            masked[k] = '***'
        else:
            masked[k] = v
    return masked


class MarkingHttpClient:
    def __init__(self, base_url: str, *, default_headers: dict | None = None, timeout: float | None = None) -> None:
        self.base_url = base_url.rstrip('/')
        self.default_headers = default_headers or {}
        self.timeout = timeout or settings.crpt_http_timeout

    def request(
        self,
        method: str,
        path: str,
        *,
        headers: dict | None = None,
        params: dict | None = None,
        json: dict | list | None = None,
        content: bytes | None = None,
        idempotency_key: str | None = None,
        correlation_id: str | None = None,
        expected_status: tuple[int, ...] = (200, 201),
    ) -> httpx.Response:
        corr = correlation_id or new_correlation_id()
        merged = {**self.default_headers, **(headers or {}), 'X-Correlation-Id': corr}
        if idempotency_key:
            merged['X-Idempotency-Key'] = idempotency_key
        url = f'{self.base_url}{path}'

        attempts = _MAX_SAFE_RETRIES if method.upper() in _SAFE_RETRY_METHODS else 1
        last_exc: Exception | None = None
        for attempt in range(1, attempts + 1):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    resp = client.request(
                        method, url, headers=merged, params=params, json=json, content=content
                    )
                logger.info(
                    'marking.http %s %s -> %s [corr=%s attempt=%s headers=%s]',
                    method,
                    path,
                    resp.status_code,
                    corr,
                    attempt,
                    _mask_headers(merged),
                )
                if resp.status_code == 401:
                    raise ExternalAuthError(correlation_id=corr, details={'status': 401})
                if resp.status_code == 429:
                    raise RateLimitedError(correlation_id=corr, details={'status': 429})
                if resp.status_code not in expected_status:
                    raise ExternalApiError(
                        f'Внешняя система вернула {resp.status_code}',
                        correlation_id=corr,
                        details={'status': resp.status_code, 'body': resp.text[:500]},
                    )
                return resp
            except (httpx.TimeoutException, httpx.TransportError) as exc:
                last_exc = exc
                if method.upper() not in _SAFE_RETRY_METHODS or attempt == attempts:
                    raise ExternalApiError(
                        'Сетевая ошибка обращения к внешней системе',
                        correlation_id=corr,
                        details={'error': type(exc).__name__},
                    ) from exc
        # недостижимо, но для типизации
        raise ExternalApiError('Сетевая ошибка', correlation_id=corr) from last_exc
