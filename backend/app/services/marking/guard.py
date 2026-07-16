"""Предохранители окружения для юридически значимых операций.

По умолчанию: sandbox, продакшн запрещён, dry-run включён. Если CRPT_ENV=production,
но CRPT_ALLOW_PRODUCTION!=true — контролируемая ошибка. Юридически значимые операции
(отправка отчётов/документов/заказов) не выполняются в dry-run.
"""

from __future__ import annotations

from app.config import settings
from app.services.marking.errors import ProductionBlockedError


def is_production() -> bool:
    return settings.crpt_env.lower() == 'production'


def assert_environment_ok() -> None:
    if is_production() and not settings.crpt_allow_production:
        raise ProductionBlockedError(
            'CRPT_ENV=production, но CRPT_ALLOW_PRODUCTION != true',
            details={'crpt_env': settings.crpt_env},
        )


def assert_legal_operation_allowed() -> None:
    """Гейт для юридически значимых внешних вызовов (отправка/подпись во внешнюю систему)."""
    assert_environment_ok()
    if settings.crpt_dry_run:
        raise ProductionBlockedError(
            'CRPT_DRY_RUN=true: юридически значимые операции отключены',
            details={'dry_run': True},
        )


def is_dry_run() -> bool:
    return settings.crpt_dry_run
