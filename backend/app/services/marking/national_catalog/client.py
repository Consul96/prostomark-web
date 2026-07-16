"""Клиент Национального каталога (карточки товаров, GTIN, фиды, модерация).

Endpoint'ы НК (`апи.национальный-каталог.рф`) не входят в предоставленные PDF
(True API + СУЗ). Поэтому операции помечены NOT_IMPLEMENTED до сверки с отдельной
документацией НК. Интерфейс зафиксирован, чтобы feed/gtin/moderation-сервисы
опирались на стабильный контракт.
"""

from __future__ import annotations

from app.services.marking.errors import NotImplementedIntegrationError

_REASON = (
    'API Национального каталога не подтверждён предоставленной документацией '
    '(True API / СУЗ). Требуется отдельная спецификация НК. Реализация — Phase 2.'
)


class NationalCatalogClient:
    def __init__(self, *, token_provider) -> None:
        self._token_provider = token_provider

    def reserve_gtin(self, card_payload: dict) -> dict:
        raise NotImplementedIntegrationError(_REASON, details={'method': 'reserve_gtin'})

    def send_feed(self, feed_payload: dict) -> dict:
        raise NotImplementedIntegrationError(_REASON, details={'method': 'send_feed'})

    def get_feed_status(self, feed_id: str) -> dict:
        raise NotImplementedIntegrationError(_REASON, details={'method': 'get_feed_status'})

    def publish(self, good_id: str, *, signature: str) -> dict:
        raise NotImplementedIntegrationError(_REASON, details={'method': 'publish'})
