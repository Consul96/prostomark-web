"""Зашифрованное файловое хранилище полных КМ и чувствительных выгрузок.

Authenticated encryption (AES-256-GCM). Открытые КМ не попадают ни в БД-индексы,
ни в логи — только в зашифрованные файлы под marking_storage_path.

Формат файла: [12 байт nonce][ciphertext+tag]. Ключ — marking_encryption_key
(base64-urlsafe 32 байта). При пустом ключе генерируется эфемерный (dev-режим),
что делает ранее зашифрованные файлы нечитаемыми — для production ключ обязателен.
"""

from __future__ import annotations

import base64
import hashlib
import os
import secrets
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.config import settings

_NONCE_BYTES = 12


def _load_key() -> bytes:
    raw = settings.marking_encryption_key.strip()
    if not raw:
        # dev-режим: эфемерный ключ (не для production).
        return secrets.token_bytes(32)
    try:
        key = base64.urlsafe_b64decode(raw)
    except Exception:  # noqa: BLE001
        key = hashlib.sha256(raw.encode('utf-8')).digest()
    if len(key) not in (16, 24, 32):
        key = hashlib.sha256(key).digest()
    return key


class EncryptedStorage:
    def __init__(self, base_path: Path | None = None, key: bytes | None = None) -> None:
        self.base_path = Path(base_path or settings.marking_storage_path)
        self._key = key or _load_key()

    # --- низкоуровневое шифрование байтов ---
    def encrypt_bytes(self, plaintext: bytes) -> bytes:
        nonce = os.urandom(_NONCE_BYTES)
        ct = AESGCM(self._key).encrypt(nonce, plaintext, None)
        return nonce + ct

    def decrypt_bytes(self, blob: bytes) -> bytes:
        nonce, ct = blob[:_NONCE_BYTES], blob[_NONCE_BYTES:]
        return AESGCM(self._key).decrypt(nonce, ct, None)

    # --- файловые операции ---
    def _resolve(self, rel_path: str) -> Path:
        # Защита от path traversal: результат обязан лежать внутри base_path.
        target = (self.base_path / rel_path).resolve()
        base = self.base_path.resolve()
        if base not in target.parents and target != base:
            raise ValueError('Path traversal detected')
        return target

    def write(self, rel_path: str, plaintext: bytes) -> tuple[str, str]:
        """Шифрует и пишет файл. Возвращает (rel_path, sha256 зашифрованного файла)."""
        target = self._resolve(rel_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        blob = self.encrypt_bytes(plaintext)
        target.write_bytes(blob)
        digest = hashlib.sha256(blob).hexdigest()
        return rel_path, digest

    def read(self, rel_path: str, *, expected_hash: str | None = None) -> bytes:
        target = self._resolve(rel_path)
        blob = target.read_bytes()
        if expected_hash is not None:
            actual = hashlib.sha256(blob).hexdigest()
            if not secrets.compare_digest(actual, expected_hash):
                raise ValueError('Encrypted file hash mismatch')
        return self.decrypt_bytes(blob)

    def write_km_codes(self, rel_path: str, codes: list[str]) -> tuple[str, str]:
        """Записывает список полных КМ (по одному в строке, без потери GS)."""
        payload = '\n'.join(codes).encode('utf-8')
        return self.write(rel_path, payload)

    def read_km_codes(self, rel_path: str, *, expected_hash: str | None = None) -> list[str]:
        raw = self.read(rel_path, expected_hash=expected_hash).decode('utf-8')
        return [line for line in raw.split('\n') if line]


def get_storage() -> EncryptedStorage:
    return EncryptedStorage()
