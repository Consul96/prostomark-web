"""Проверка МЧД клиента.

Определяет статус доверенности по срокам и (в боевом режиме) по данным True API.
Здесь — детерминированная проверка по сохранённым срокам; сетевая проверка через
True API (список МЧД) помечена как требующая подтверждения endpoint'а.
"""

from __future__ import annotations

from datetime import date

from app.models.enums import MchdStatus
from app.models.marking import CrptClient


def evaluate_mchd_status(client: CrptClient, *, today: date | None = None) -> str:
    today = today or date.today()
    if not client.mchd_number:
        return MchdStatus.NOT_SET.value
    if client.mchd_valid_until and client.mchd_valid_until < today:
        return MchdStatus.EXPIRED.value
    if client.mchd_valid_from and client.mchd_valid_from > today:
        return MchdStatus.NOT_SET.value
    return MchdStatus.ACTIVE.value


def assert_mchd_active(client: CrptClient) -> None:
    from app.services.marking.errors import MchdExpiredError

    if evaluate_mchd_status(client) != MchdStatus.ACTIVE.value:
        raise MchdExpiredError(details={'client_id': str(client.id), 'mchd_number': client.mchd_number})
