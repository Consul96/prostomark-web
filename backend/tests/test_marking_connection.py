"""Тесты sandbox connection test (True API + СУЗ через МЧД + Sign Agent).

Сеть к реальному стенду не дёргаем: подменяем MarkingHttpClient.request каноничными
ответами. Проверяем: реальный поток challenge→sign→signIn, создание SignJob,
раздельные кеши, ЧЕСТНЫЙ статус, продакшн-блокировку.
"""

from __future__ import annotations

import uuid
from datetime import date, timedelta

import pytest

from app.config import settings
from app.models.enums import SignJobStatus
from app.models.marking import CrptClient, SignerAgent, SignJob
from app.security.tokens import hash_token
from app.services.marking import http_client as http_mod
from app.services.marking.clients import connection_service
from app.services.marking.errors import ExternalApiError, ProductionBlockedError
from tests.conftest import auth_headers

BASE = '/api/v1/marking'


class _Resp:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


def _fake_request_success(self, method, path, **kwargs):
    if path.endswith('/auth/key'):
        return _Resp({'uuid': str(uuid.uuid4()), 'data': 'challenge-data-to-sign'})
    if 'simpleSignIn' in path:
        # True API отдаёт token, СУЗ — clientToken
        if 'true-api' in self.base_url:
            return _Resp({'token': 'TA-TOKEN'})
        return _Resp({'clientToken': 'SUZ-CLIENT-TOKEN'})
    raise AssertionError(f'unexpected {method} {path}')


def _fake_request_network_error(self, method, path, **kwargs):
    raise ExternalApiError('network down', details={'error': 'timeout'})


def _make_ready_client(db, company_id) -> CrptClient:
    agent = SignerAgent(company_id=company_id, name='A', api_key_hash=hash_token('k'), is_active=True)
    db.add(agent)
    db.flush()
    client = CrptClient(
        company_id=company_id,
        name='ООО Готовый',
        inn='7701234567',
        environment='sandbox',
        product_groups=['lp'],
        oms_id='OMS-1',
        oms_connection='conn-A',
        signer_agent_id=agent.id,
        mchd_number='МЧД-1',
        mchd_valid_from=date.today() - timedelta(days=1),
        mchd_valid_until=date.today() + timedelta(days=30),
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def test_connection_success_reports_ok_and_separate_caches(db, seed, monkeypatch):
    monkeypatch.setattr(http_mod.MarkingHttpClient, 'request', _fake_request_success)
    client = _make_ready_client(db, seed['company_a'].id)

    result = connection_service.run_connection_test(db, client)

    assert result['mchd']['status'] == 'active'
    assert result['true_api']['status'] == 'ok'
    assert result['suz']['status'] == 'ok'
    # Раздельные кеши токенов
    assert result['true_api']['cache_key'].startswith('true-api:')
    assert result['suz']['cache_key'].startswith('suz:')
    assert result['suz']['cache_key'].endswith(':conn-A')  # включает omsConnection
    assert result['token_caches_separated'] is True

    # Поток реально прошёл через Sign Agent: attached SignJob'ы созданы и завершены
    jobs = db.query(SignJob).filter(SignJob.crpt_client_id == client.id).all()
    assert len(jobs) == 2
    assert {j.sign_type for j in jobs} == {'attached'}
    assert all(j.status == SignJobStatus.COMPLETED.value for j in jobs)
    # Клиент обновлён честным статусом
    db.refresh(client)
    assert client.true_api_status == 'ok'
    assert client.suz_status == 'ok'


def test_connection_network_failure_is_honest_not_connected(db, seed, monkeypatch):
    monkeypatch.setattr(http_mod.MarkingHttpClient, 'request', _fake_request_network_error)
    client = _make_ready_client(db, seed['company_a'].id)

    result = connection_service.run_connection_test(db, client)

    # Конфигурация заполнена, но токен не получен → НЕ ok
    assert result['true_api']['status'] == 'unavailable'
    assert result['suz']['status'] == 'unavailable'
    db.refresh(client)
    assert client.true_api_status != 'ok'
    assert client.suz_status != 'ok'


def test_connection_missing_prereq_needs_setup_no_network(db, seed, monkeypatch):
    # Если дёрнется сеть — упадём; значит needs_setup вычислен без сетевых вызовов.
    def _boom(*a, **k):
        raise AssertionError('network must not be called when prereqs missing')

    monkeypatch.setattr(http_mod.MarkingHttpClient, 'request', _boom)
    client = CrptClient(
        company_id=seed['company_a'].id, name='ООО Пусто', inn='7700000000', environment='sandbox',
        product_groups=['lp'],  # нет МЧД, нет агента, нет oms
    )
    db.add(client)
    db.commit()
    db.refresh(client)

    result = connection_service.run_connection_test(db, client)
    assert result['mchd']['status'] in ('not_set',)
    assert result['true_api']['status'] == 'needs_setup'
    assert result['suz']['status'] == 'needs_setup'


def test_connection_blocks_production(db, seed, monkeypatch):
    monkeypatch.setattr(settings, 'crpt_env', 'production')
    monkeypatch.setattr(settings, 'crpt_allow_production', False)
    client = _make_ready_client(db, seed['company_a'].id)
    with pytest.raises(ProductionBlockedError):
        connection_service.run_connection_test(db, client)


def test_connection_endpoint_smoke(client, seed, monkeypatch):
    monkeypatch.setattr(http_mod.MarkingHttpClient, 'request', _fake_request_success)
    h = auth_headers(seed['users']['company_admin'])
    cid = client.post(f'{BASE}/clients', headers=h, json={
        'name': 'X', 'inn': '7701234567', 'environment': 'sandbox', 'product_groups': ['lp'],
        'oms_id': 'OMS', 'oms_connection': 'conn-X',
        'mchd_number': 'M1', 'mchd_valid_until': str(date.today() + timedelta(days=10)),
    }).json()['id']
    # Без агента и в dry-run подпись — mock; True API вернёт токен (в тесте подменён) → ok
    r = client.post(f'{BASE}/clients/{cid}/sandbox-connection-test', headers=h)
    assert r.status_code == 200
    body = r.json()
    assert 'true_api' in body and 'suz' in body
    assert body['token_caches_separated'] is True
