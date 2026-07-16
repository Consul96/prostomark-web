"""Работа с кодами маркировки (КМ): три представления кода.

Всегда различаем:
  * km_original — точный полный код (включая криптохвост и разделители GS `\\x1d`);
  * km_lookup   — нормализованное представление (только для методов, где это
                  допускает API); GS удаляются, регистр не меняется;
  * km_hash     — HMAC-SHA256(km_original) для поиска дублей без хранения кода.

НИКОГДА не удаляем `\\x1d` из значения, предназначенного для СУЗ / печати / выгрузки.
km_original хранится только в зашифрованном файловом хранилище, не в БД-индексах.
"""

from __future__ import annotations

import hashlib
import hmac

GS = '\x1d'  # ASCII Group Separator (FNC1)


def km_lookup(km_original: str) -> str:
    """Нормализованное представление КМ для методов, где API это допускает.

    Убирает служебные разделители GS. Возвращает исходный код без GS.
    Использовать ТОЛЬКО для сравнения/поиска — не для отправки в СУЗ.
    """
    return km_original.replace(GS, '').replace('', '').strip()


def km_hash(km_original: str, secret: str) -> str:
    """HMAC-SHA256 полного КМ (hex). Ключ — marking_encryption_key."""
    return hmac.new(secret.encode('utf-8'), km_original.encode('utf-8'), hashlib.sha256).hexdigest()


def mask_km(km_original: str, *, keep_prefix: int = 4, keep_suffix: int = 3) -> str:
    """Маскированное представление КМ для UI/логов (полный код не раскрывается)."""
    code = km_lookup(km_original)
    if len(code) <= keep_prefix + keep_suffix:
        return '*' * len(code)
    return f'{code[:keep_prefix]}…{code[-keep_suffix:]}'


def parse_gtin_from_km(km_original: str) -> str | None:
    """Извлекает GTIN (AI 01, 14 цифр) из DataMatrix КМ, если код начинается с `01`."""
    code = km_lookup(km_original)
    if code.startswith('01') and len(code) >= 16 and code[2:16].isdigit():
        return code[2:16]
    return None
