"""Интеграционные тесты API модуля marking: smoke, изоляция, роли, Sign Agent."""

from __future__ import annotations

import base64
import uuid
from datetime import UTC, datetime, timedelta

import pytest

from app.models.enums import SignJobStatus
from app.models.marking import SignerAgent, SignJob
from app.security.tokens import hash_token
from app.services.marking.auth.sign_service import MockSigner, payload_sha256
from tests.conftest import auth_headers

BASE = '/api/v1/marking'


def _client_payload(inn='7701234567', **extra):
    return {'name': 'ООО Тест', 'inn': inn, 'environment': 'sandbox', 'product_groups': ['lp'], **extra}


# =====================================================================
# 5. SMOKE — все группы маршрутов
# =====================================================================


def test_smoke_all_marking_routes(client, seed):
    admin = seed['users']['company_admin']
    h = auth_headers(admin)

    # dashboard
    r = client.get(f'{BASE}/dashboard', headers=h)
    assert r.status_code == 200
    assert 'active_applications' in r.json()

    # clients: list empty, create, get, patch, check-connection
    assert client.get(f'{BASE}/clients', headers=h).json() == []
    created = client.post(f'{BASE}/clients', headers=h, json=_client_payload(oms_id='OMS1', oms_connection='conn1', signer_agent_id=None))
    assert created.status_code == 201
    cid = created.json()['id']
    assert client.get(f'{BASE}/clients/{cid}', headers=h).status_code == 200
    assert client.patch(f'{BASE}/clients/{cid}', headers=h, json={'name': 'ООО Тест 2'}).json()['name'] == 'ООО Тест 2'
    cc = client.post(f'{BASE}/clients/{cid}/check-connection', headers=h)
    assert cc.status_code == 200
    assert set(cc.json()) == {'mchd_status', 'true_api_status', 'suz_status'}

    # applications
    assert client.get(f'{BASE}/applications', headers=h).json() == []
    app_created = client.post(
        f'{BASE}/applications', headers=h, json={'crpt_client_id': cid, 'title': 'Заявка 1', 'product_group': 'lp'}
    )
    assert app_created.status_code == 201
    aid = app_created.json()['id']
    assert client.get(f'{BASE}/applications/{aid}', headers=h).status_code == 200
    assert client.patch(f'{BASE}/applications/{aid}', headers=h, json={'status': 'in_progress'}).json()['status'] == 'in_progress'

    # sign-agent agents
    agent = client.post(f'{BASE}/sign-agent/agents', headers=h, json={'name': 'Agent-1'})
    assert agent.status_code == 201
    assert agent.json()['api_key']  # показывается один раз
    assert len(client.get(f'{BASE}/sign-agent/agents', headers=h).json()) == 1

    # jobs / sign-jobs / history
    assert client.get(f'{BASE}/jobs', headers=h).status_code == 200
    assert client.get(f'{BASE}/sign-agent/jobs', headers=h).status_code == 200
    assert client.get(f'{BASE}/history', headers=h).status_code == 200


def test_dashboard_reflects_created_data(client, seed):
    h = auth_headers(seed['users']['manager'])
    cid = client.post(f'{BASE}/clients', headers=h, json=_client_payload()).json()['id']
    client.post(f'{BASE}/applications', headers=h, json={'crpt_client_id': cid, 'title': 'A', 'product_group': 'lp'})
    d = client.get(f'{BASE}/dashboard', headers=h).json()
    assert d['active_applications'] == 0  # черновик, не in_progress


# =====================================================================
# 6/8. ИЗОЛЯЦИЯ АРЕНДАТОРОВ
# =====================================================================


def test_isolation_client_cross_company(client, seed):
    # Клиент создан в компании B
    hb = auth_headers(seed['user_b'])
    cid = client.post(f'{BASE}/clients', headers=hb, json=_client_payload(inn='7809999999')).json()['id']

    # Пользователь компании A не видит и не может получить клиента B
    ha = auth_headers(seed['users']['company_admin'])
    assert client.get(f'{BASE}/clients', headers=ha).json() == []
    assert client.get(f'{BASE}/clients/{cid}', headers=ha).status_code == 404
    assert client.patch(f'{BASE}/clients/{cid}', headers=ha, json={'name': 'hack'}).status_code == 404
    assert client.post(f'{BASE}/clients/{cid}/check-connection', headers=ha).status_code == 404


def test_isolation_application_cross_company(client, seed):
    hb = auth_headers(seed['user_b'])
    cid = client.post(f'{BASE}/clients', headers=hb, json=_client_payload(inn='7811111111')).json()['id']
    aid = client.post(f'{BASE}/applications', headers=hb, json={'crpt_client_id': cid, 'title': 'B-app', 'product_group': 'lp'}).json()['id']

    ha = auth_headers(seed['users']['manager'])
    assert client.get(f'{BASE}/applications', headers=ha).json() == []
    assert client.get(f'{BASE}/applications/{aid}', headers=ha).status_code == 404


def test_isolation_application_cannot_use_foreign_client(client, seed):
    # Клиент компании B; менеджер компании A пытается создать заявку на него (подмена UUID).
    hb = auth_headers(seed['user_b'])
    cid_b = client.post(f'{BASE}/clients', headers=hb, json=_client_payload(inn='7822222222')).json()['id']
    ha = auth_headers(seed['users']['manager'])
    r = client.post(f'{BASE}/applications', headers=ha, json={'crpt_client_id': cid_b, 'title': 'x', 'product_group': 'lp'})
    assert r.status_code == 404  # клиент не найден в company_a


def test_isolation_signer_agent_and_jobs(client, seed, db):
    # Агент компании B
    hb = auth_headers(seed['user_b'])
    client.post(f'{BASE}/sign-agent/agents', headers=hb, json={'name': 'B-agent'})
    ha = auth_headers(seed['users']['company_admin'])
    assert client.get(f'{BASE}/sign-agent/agents', headers=ha).json() == []
    assert client.get(f'{BASE}/sign-agent/jobs', headers=ha).json() == []

    # SignJob компании B не виден в списке компании A
    _seed_sign_job(db, seed['company_b'].id)
    assert client.get(f'{BASE}/sign-agent/jobs', headers=ha).json() == []
    assert len(client.get(f'{BASE}/sign-agent/jobs', headers=hb).json()) == 1


def test_isolation_history_cross_company(client, seed):
    hb = auth_headers(seed['user_b'])
    client.post(f'{BASE}/clients', headers=hb, json=_client_payload(inn='7833333333'))  # пишет в лог компании B
    ha = auth_headers(seed['users']['company_admin'])
    assert client.get(f'{BASE}/history', headers=ha).json() == []
    assert len(client.get(f'{BASE}/history', headers=hb).json()) >= 1


# =====================================================================
# 9. РОЛИ
# =====================================================================


def test_roles_view_allowed_for_all(client, seed):
    for role in ('superadmin', 'company_admin', 'manager', 'user'):
        h = auth_headers(seed['users'][role])
        assert client.get(f'{BASE}/clients', headers=h).status_code == 200
        assert client.get(f'{BASE}/dashboard', headers=h).status_code == 200


def test_roles_user_cannot_create_client(client, seed):
    h = auth_headers(seed['users']['user'])
    assert client.post(f'{BASE}/clients', headers=h, json=_client_payload()).status_code == 403


def test_roles_manager_can_create_but_not_deactivate(client, seed):
    hm = auth_headers(seed['users']['manager'])
    cid = client.post(f'{BASE}/clients', headers=hm, json=_client_payload()).json()['id']
    # deactivate требует company_admin
    assert client.post(f'{BASE}/clients/{cid}/deactivate', headers=hm).status_code == 403


def test_roles_company_admin_can_deactivate(client, seed):
    ha = auth_headers(seed['users']['company_admin'])
    cid = client.post(f'{BASE}/clients', headers=ha, json=_client_payload()).json()['id']
    assert client.post(f'{BASE}/clients/{cid}/deactivate', headers=ha).json()['is_active'] is False


def test_roles_only_admin_creates_agent(client, seed):
    assert client.post(f'{BASE}/sign-agent/agents', headers=auth_headers(seed['users']['manager']), json={'name': 'x'}).status_code == 403
    assert client.post(f'{BASE}/sign-agent/agents', headers=auth_headers(seed['users']['company_admin']), json={'name': 'x'}).status_code == 201


def test_no_auth_rejected(client):
    assert client.get(f'{BASE}/clients').status_code in (401, 403)


# =====================================================================
# 7/13. SIGN AGENT — протокол (mock signer, 10 кейсов)
# =====================================================================


def _register_agent(client, headers, name='Agent') -> tuple[str, str]:
    r = client.post(f'{BASE}/sign-agent/agents', headers=headers, json={'name': name})
    body = r.json()
    return body['id'], body['api_key']


def _seed_sign_job(db, company_id, *, payload=b'sign-me', detached=True, expires_in=900, agent_id=None) -> SignJob:
    job = SignJob(
        company_id=company_id,
        sign_type='detached' if detached else 'attached',
        payload_base64=base64.b64encode(payload).decode(),
        payload_sha256=payload_sha256(payload),
        status=SignJobStatus.PENDING.value,
        signer_agent_id=agent_id,
        expires_at=datetime.now(UTC) + timedelta(seconds=expires_in),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def test_agent_registration_and_key_hashed(client, seed, db):
    h = auth_headers(seed['users']['company_admin'])
    agent_id, api_key = _register_agent(client, h)
    row = db.get(SignerAgent, uuid.UUID(agent_id))
    # Сырой ключ не хранится — только HMAC-хеш.
    assert row.api_key_hash == hash_token(api_key)
    assert row.api_key_hash != api_key


def test_agent_heartbeat(client, seed, db):
    h = auth_headers(seed['users']['company_admin'])
    agent_id, api_key = _register_agent(client, h)
    r = client.post(f'{BASE}/sign-agent/heartbeat', headers={'X-Agent-Api-Key': api_key})
    assert r.status_code == 200
    assert db.get(SignerAgent, uuid.UUID(agent_id)).last_heartbeat_at is not None


def test_agent_job_polling_claims_pending(client, seed, db):
    h = auth_headers(seed['users']['company_admin'])
    _, api_key = _register_agent(client, h)
    job = _seed_sign_job(db, seed['company_a'].id)
    r = client.get(f'{BASE}/sign-agent/next-job', headers={'X-Agent-Api-Key': api_key})
    body = r.json()
    assert body['job_id'] == str(job.id)
    assert body['payload_sha256'] == job.payload_sha256
    db.refresh(job)
    assert job.status == SignJobStatus.CLAIMED.value
    # Следующий опрос — пусто
    assert client.get(f'{BASE}/sign-agent/next-job', headers={'X-Agent-Api-Key': api_key}).json()['job_id'] is None


def test_agent_detached_signature_result(client, seed, db):
    h = auth_headers(seed['users']['company_admin'])
    _, api_key = _register_agent(client, h)
    job = _seed_sign_job(db, seed['company_a'].id, detached=True)
    claim = client.get(f'{BASE}/sign-agent/next-job', headers={'X-Agent-Api-Key': api_key}).json()
    payload = base64.b64decode(claim['payload_base64'])
    sig = MockSigner().sign(payload, detached=True, thumbprint=None)
    r = client.post(f'{BASE}/sign-agent/result', headers={'X-Agent-Api-Key': api_key},
                    json={'job_id': claim['job_id'], 'signature_base64': sig, 'payload_sha256': payload_sha256(payload)})
    assert r.status_code == 200
    db.refresh(job)
    assert job.status == SignJobStatus.COMPLETED.value
    assert base64.b64decode(job.signature_base64).startswith(b'MOCK-DETACHED:')


def test_agent_attached_signature_result(client, seed, db):
    h = auth_headers(seed['users']['company_admin'])
    _, api_key = _register_agent(client, h)
    job = _seed_sign_job(db, seed['company_a'].id, detached=False)
    claim = client.get(f'{BASE}/sign-agent/next-job', headers={'X-Agent-Api-Key': api_key}).json()
    payload = base64.b64decode(claim['payload_base64'])
    sig = MockSigner().sign(payload, detached=False, thumbprint=None)
    r = client.post(f'{BASE}/sign-agent/result', headers={'X-Agent-Api-Key': api_key},
                    json={'job_id': claim['job_id'], 'signature_base64': sig, 'payload_sha256': payload_sha256(payload)})
    assert r.status_code == 200
    db.refresh(job)
    assert base64.b64decode(job.signature_base64).startswith(b'MOCK-ATTACHED:')


def test_agent_incorrect_api_key(client, seed, db):
    _seed_sign_job(db, seed['company_a'].id)
    assert client.get(f'{BASE}/sign-agent/next-job', headers={'X-Agent-Api-Key': 'wrong-key'}).status_code == 401
    assert client.post(f'{BASE}/sign-agent/heartbeat', headers={'X-Agent-Api-Key': 'wrong-key'}).status_code == 401


def test_agent_payload_hash_mismatch_rejected(client, seed, db):
    h = auth_headers(seed['users']['company_admin'])
    _, api_key = _register_agent(client, h)
    job = _seed_sign_job(db, seed['company_a'].id)
    client.get(f'{BASE}/sign-agent/next-job', headers={'X-Agent-Api-Key': api_key})
    r = client.post(f'{BASE}/sign-agent/result', headers={'X-Agent-Api-Key': api_key},
                    json={'job_id': str(job.id), 'signature_base64': 'x', 'payload_sha256': 'deadbeef'})
    assert r.status_code == 409
    assert r.json()['code'] == 'MARKING_PAYLOAD_HASH_MISMATCH'
    db.refresh(job)
    assert job.status != SignJobStatus.COMPLETED.value


def test_agent_expired_job(client, seed, db):
    h = auth_headers(seed['users']['company_admin'])
    _, api_key = _register_agent(client, h)
    job = _seed_sign_job(db, seed['company_a'].id, expires_in=-10)  # уже истёк
    # next-job не выдаёт просроченную задачу
    assert client.get(f'{BASE}/sign-agent/next-job', headers={'X-Agent-Api-Key': api_key}).json()['job_id'] is None
    # прямой результат по просроченной задаче отклоняется
    r = client.post(f'{BASE}/sign-agent/result', headers={'X-Agent-Api-Key': api_key},
                    json={'job_id': str(job.id), 'signature_base64': 'x', 'payload_sha256': job.payload_sha256})
    assert r.status_code == 409
    db.refresh(job)
    assert job.status == SignJobStatus.EXPIRED.value


def test_agent_duplicate_result(client, seed, db):
    h = auth_headers(seed['users']['company_admin'])
    _, api_key = _register_agent(client, h)
    job = _seed_sign_job(db, seed['company_a'].id)
    claim = client.get(f'{BASE}/sign-agent/next-job', headers={'X-Agent-Api-Key': api_key}).json()
    payload = base64.b64decode(claim['payload_base64'])
    body = {'job_id': claim['job_id'], 'signature_base64': MockSigner().sign(payload, detached=True, thumbprint=None),
            'payload_sha256': payload_sha256(payload)}
    assert client.post(f'{BASE}/sign-agent/result', headers={'X-Agent-Api-Key': api_key}, json=body).status_code == 200
    # Повтор того же результата — идемпотентно ok
    dup = client.post(f'{BASE}/sign-agent/result', headers={'X-Agent-Api-Key': api_key}, json=body)
    assert dup.status_code == 200
    assert dup.json().get('idempotent') is True
    # Повтор с другим payload_sha256 (переопределение завершённой задачи) — 409
    body2 = {**body, 'payload_sha256': 'ffff'}
    assert client.post(f'{BASE}/sign-agent/result', headers={'X-Agent-Api-Key': api_key}, json=body2).status_code == 409


def test_agent_unavailable_deactivated(client, seed, db):
    h = auth_headers(seed['users']['company_admin'])
    agent_id, api_key = _register_agent(client, h)
    # Деактивируем агента
    db.get(SignerAgent, uuid.UUID(agent_id)).is_active = False
    db.commit()
    _seed_sign_job(db, seed['company_a'].id)
    assert client.get(f'{BASE}/sign-agent/next-job', headers={'X-Agent-Api-Key': api_key}).status_code == 401
