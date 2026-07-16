"""Клиент СУЗ (API СУЗ 3.0). Заказ, статус, получение и списание КМ.

Подтверждённые документацией endpoint'ы (см. crpt-api-mapping.md):
  * POST /api/v3/order?omsId={omsId}        — создать заказ на эмиссию КМ
  * GET  /api/v3/order?omsId={omsId}         — статус заказа
  * GET  /api/v3/codes?omsId={omsId}&orderId=&gtin=&quantity=&lastBlockId=  — получить КМ
  * POST /api/v3/utilisation?omsId={omsId}   — отчёт о нанесении (ручной; НЕ для лп/обуви)
  * GET  /api/v3/ping?omsId={omsId}          — проверка доступности

Заголовки: clientToken: <SUZ clientToken>. omsId — из настроек клиента.

Статус реализации: интерфейс готов; фактические запросы выполняются только когда
подтверждены схемы тел (create order / utilisation) и снят предохранитель окружения.
До этого методы поднимают NotImplementedIntegrationError с явной причиной.
"""

from __future__ import annotations

from app.services.marking.errors import NotImplementedIntegrationError

_REASON = (
    'Тела запросов СУЗ (create order / получение КМ / utilisation) требуют сверки со '
    'схемами API СУЗ 3.0 и снятия предохранителя окружения. Реализация — Phase 3.'
)


class SuzClient:
    def __init__(self, *, oms_id: str, client_token_provider) -> None:
        self.oms_id = oms_id
        self._token_provider = client_token_provider

    def ping(self) -> dict:
        raise NotImplementedIntegrationError(_REASON, details={'method': 'ping'})

    def create_order(self, order_payload: dict, *, idempotency_key: str) -> dict:
        raise NotImplementedIntegrationError(_REASON, details={'method': 'create_order'})

    def get_order_status(self, order_id: str) -> dict:
        raise NotImplementedIntegrationError(_REASON, details={'method': 'get_order_status'})

    def get_codes(self, *, order_id: str, gtin: str, quantity: int, last_block_id: str | None = None) -> dict:
        raise NotImplementedIntegrationError(_REASON, details={'method': 'get_codes'})

    def send_utilisation_report(self, report_payload: dict, *, signature: str) -> dict:
        raise NotImplementedIntegrationError(_REASON, details={'method': 'send_utilisation_report'})
