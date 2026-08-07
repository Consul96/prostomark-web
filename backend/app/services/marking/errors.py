"""Нормализованные ошибки модуля marking.

Единый формат API-ответа об ошибке:
    {"code": "MARKING_ERROR_CODE", "message": "...", "details": {}, "correlation_id": "..."}
Пользователю не показывается сырой traceback; техническая причина логируется серверно.
"""

from __future__ import annotations


class MarkingError(Exception):
    """Базовая ошибка модуля. http_status по умолчанию 400."""

    code = 'MARKING_ERROR'
    http_status = 400
    message = 'Ошибка модуля маркировки'

    def __init__(
        self,
        message: str | None = None,
        *,
        code: str | None = None,
        details: dict | None = None,
        correlation_id: str | None = None,
        http_status: int | None = None,
    ) -> None:
        self.message = message or self.message
        self.code = code or self.code
        self.details = details or {}
        self.correlation_id = correlation_id
        if http_status is not None:
            self.http_status = http_status
        super().__init__(self.message)

    def to_dict(self) -> dict:
        return {
            'code': self.code,
            'message': self.message,
            'details': self.details,
            'correlation_id': self.correlation_id,
        }


class NotImplementedIntegrationError(MarkingError):
    """Операция не подтверждена документацией — интеграция помечена NOT_IMPLEMENTED."""

    code = 'MARKING_NOT_IMPLEMENTED'
    http_status = 501
    message = 'Операция ещё не подтверждена документацией и недоступна'


class ProductionBlockedError(MarkingError):
    """Продакшн-вызов запрещён (CRPT_ALLOW_PRODUCTION!=true или CRPT_DRY_RUN)."""

    code = 'MARKING_PRODUCTION_BLOCKED'
    http_status = 409
    message = 'Продакшн-операции ГИС МТ отключены предохранителем окружения'


class InvalidStateTransitionError(MarkingError):
    code = 'MARKING_INVALID_STATE_TRANSITION'
    http_status = 409
    message = 'Недопустимый переход статуса'


class MchdExpiredError(MarkingError):
    code = 'MARKING_MCHD_EXPIRED'
    http_status = 409
    message = 'МЧД клиента истекла или недействительна'


class SignAgentUnavailableError(MarkingError):
    code = 'MARKING_SIGN_AGENT_UNAVAILABLE'
    http_status = 409
    message = 'Sign Agent недоступен'


class PayloadHashMismatchError(MarkingError):
    code = 'MARKING_PAYLOAD_HASH_MISMATCH'
    http_status = 409
    message = 'Хеш payload не совпадает — подпись отклонена'


class ExternalApiError(MarkingError):
    """Ошибка внешней системы (True API / СУЗ / НК)."""

    code = 'MARKING_EXTERNAL_API_ERROR'
    http_status = 502
    message = 'Ошибка внешней системы ГИС МТ'


class ExternalAuthError(ExternalApiError):
    code = 'MARKING_EXTERNAL_AUTH_ERROR'
    message = 'Ошибка авторизации во внешней системе ГИС МТ'


class RateLimitedError(ExternalApiError):
    code = 'MARKING_RATE_LIMITED'
    http_status = 429
    message = 'Превышен лимит запросов внешней системы'
