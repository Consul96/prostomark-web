"""Юнит-тесты фундамента: ключи кеша токенов, шифрование, политики, sign payload."""

import base64

import pytest

from app.services.marking.auth import token_cache as tc
from app.services.marking.auth.sign_service import MockSigner, payload_sha256
from app.services.marking.policies.product_group_registry import registry
from app.services.marking.storage.encrypted_storage import EncryptedStorage


def test_true_api_and_suz_cache_keys():
    assert tc.true_api_cache_key('sandbox', 'signer1', '7701234567') == 'true-api:sandbox:signer1:7701234567'
    # СУЗ-ключ включает omsConnection (один активный токен на omsConnection).
    assert (
        tc.suz_cache_key('production', 'signer1', '7701234567', 'conn-42')
        == 'suz:production:signer1:7701234567:conn-42'
    )


def test_cached_token_freshness():
    import time

    fresh = tc.CachedToken(token='t', expires_at=time.time() + 3600)
    stale = tc.CachedToken(token='t', expires_at=time.time() + 5)
    assert fresh.is_fresh()
    assert not stale.is_fresh()  # в пределах skew=60с считается несвежим


def test_encrypted_storage_roundtrip_and_hash(tmp_path):
    storage = EncryptedStorage(base_path=tmp_path, key=b'0' * 32)
    codes = ['0104650117240408211abc\x1d93xyz\x1d', '0104650117240408211def\x1d93uvw\x1d']
    rel, digest = storage.write_km_codes('client/batch1.enc', codes)
    assert len(digest) == 64
    restored = storage.read_km_codes(rel, expected_hash=digest)
    # GS сохранены дословно.
    assert restored == codes
    assert '\x1d' in restored[0]


def test_encrypted_storage_rejects_traversal(tmp_path):
    storage = EncryptedStorage(base_path=tmp_path, key=b'0' * 32)
    with pytest.raises(ValueError):
        storage.write('../escape.enc', b'x')


def test_encrypted_storage_detects_tamper(tmp_path):
    storage = EncryptedStorage(base_path=tmp_path, key=b'0' * 32)
    rel, digest = storage.write('a.enc', b'payload')
    with pytest.raises(ValueError):
        storage.read(rel, expected_hash='0' * 64)


def test_product_group_policies_light_industry_and_shoes():
    lp = registry.require('lp')
    shoes = registry.require('shoes')
    for policy in (lp, shoes):
        assert policy.supports_gtin
        # Обе группы: авто-отчёт о нанесении, ручной /utilisation НЕ отправляется.
        assert policy.auto_application_report is True
        assert policy.manual_application_report is False


def test_mock_signer_detached_payload_hash_matches():
    payload = b'exact-bytes-to-sign'
    signature = MockSigner().sign(payload, detached=True, thumbprint=None)
    # Подпись — валидный Base64.
    decoded = base64.b64decode(signature)
    assert decoded.startswith(b'MOCK-DETACHED:')
    # Хеш payload детерминирован.
    assert payload_sha256(payload) == payload_sha256(payload)
