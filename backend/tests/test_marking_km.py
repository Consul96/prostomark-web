"""Юнит-тесты сохранности КМ и представлений кода."""

from app.services.marking import km

# Полный КМ с разделителями GS (\x1d) — типичный DataMatrix обуви/лёгкой промышленности.
FULL_KM = '0104650117240408211abcdEF\x1d93dGVz\x1d'


def test_km_lookup_strips_gs_but_original_untouched():
    original = FULL_KM
    lookup = km.km_lookup(original)
    assert km.GS not in lookup
    assert '\x1d' not in lookup
    # Исходный код НЕ мутируется.
    assert original == FULL_KM
    assert '\x1d' in original


def test_km_hash_is_stable_and_secret_dependent():
    h1 = km.km_hash(FULL_KM, 'secret-a')
    h2 = km.km_hash(FULL_KM, 'secret-a')
    h3 = km.km_hash(FULL_KM, 'secret-b')
    assert h1 == h2
    assert h1 != h3
    assert len(h1) == 64


def test_mask_km_hides_body():
    masked = km.mask_km(FULL_KM)
    assert '…' in masked
    assert '\x1d' not in masked


def test_parse_gtin_from_km():
    assert km.parse_gtin_from_km(FULL_KM) == '04650117240408'
    assert km.parse_gtin_from_km('93abc') is None
