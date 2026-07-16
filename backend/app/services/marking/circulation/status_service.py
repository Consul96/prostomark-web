"""Контроль нанесения (True API) и статусы ввода в оборот.

Подтверждённые документацией методы True API (см. crpt-api-mapping.md):
  * POST /cises/info  — общедоступная информация о КИ по списку (владелец, статус,
                        товарная группа, дата нанесения) — основа авто-контроля нанесения.

Сравнение календарной даты нанесения выполняется с приведением UTC → timezone
клиента. Полная реализация пакетной проверки — Phase 4.
"""

from __future__ import annotations

from app.services.marking.errors import NotImplementedIntegrationError

_REASON = (
    'Пакетный контроль нанесения через True API /cises/info готовится в Phase 4 '
    '(сверка владельца/статуса/товарной группы/даты). Endpoint подтверждён документацией.'
)


class CisesInfoClient:
    def __init__(self, *, token_provider, base_url: str | None = None) -> None:
        self._token_provider = token_provider
        self.base_url = base_url

    def cises_info(self, cis_list: list[str]) -> list[dict]:
        raise NotImplementedIntegrationError(_REASON, details={'method': 'cises_info', 'count': len(cis_list)})
