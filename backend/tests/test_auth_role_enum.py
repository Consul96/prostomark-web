"""Регрессионные тесты бага user_role_enum: имя члена vs значение.

Ключевое отличие от остальных тестов: схема БД создаётся НАСТОЯЩИМИ
Alembic-миграциями (subprocess `alembic upgrade head`), а не Base.metadata.create_all.
Именно против Alembic-схемы регистрация/вход падали с InvalidTextRepresentation
('COMPANY_ADMIN' не входит в user_role_enum со значениями в нижнем регистре).

Требует доступного PostgreSQL (TEST_AUTH_PG_URL, по умолчанию 127.0.0.1:5433).
Если сервер недоступен — тесты скипаются, не ломая остальной прогон.
"""

from __future__ import annotations

import os
import subprocess
import sys
import uuid
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session, sessionmaker

BACKEND_DIR = Path(__file__).resolve().parents[1]

PG_ADMIN_URL = os.environ.get(
    'TEST_AUTH_PG_URL', 'postgresql+psycopg2://postgres:postgres@127.0.0.1:5433/postgres'
)
DB_NAME = 'prostomark_auth_enum_test'
DB_URL = PG_ADMIN_URL.rsplit('/', 1)[0] + f'/{DB_NAME}'

os.environ.setdefault('JWT_SECRET', 'testsecret')


def _pg_available() -> bool:
    try:
        eng = create_engine(PG_ADMIN_URL, connect_args={'connect_timeout': 2})
        with eng.connect():
            return True
    except Exception:  # noqa: BLE001
        return False


pytestmark = pytest.mark.skipif(not _pg_available(), reason='PostgreSQL недоступен для Alembic-теста')


def _alembic(*args: str) -> subprocess.CompletedProcess:
    """Запуск alembic subprocess-ом с DATABASE_URL, указывающим на тестовую БД."""
    env = {**os.environ, 'DATABASE_URL': DB_URL, 'JWT_SECRET': 'testsecret'}
    return subprocess.run(
        [sys.executable, '-m', 'alembic', *args],
        cwd=BACKEND_DIR,
        env=env,
        capture_output=True,
        text=True,
    )


@pytest.fixture(scope='module')
def alembic_db():
    """Полностью чистая БД + alembic upgrade head. В конце — drop."""
    admin = create_engine(PG_ADMIN_URL, isolation_level='AUTOCOMMIT')
    with admin.connect() as conn:
        conn.execute(text(f'DROP DATABASE IF EXISTS {DB_NAME} WITH (FORCE)'))
        conn.execute(text(f'CREATE DATABASE {DB_NAME}'))

    result = _alembic('upgrade', 'head')
    assert result.returncode == 0, f'alembic upgrade head failed:\n{result.stderr}'

    engine = create_engine(DB_URL)
    yield engine
    engine.dispose()
    with admin.connect() as conn:
        conn.execute(text(f'DROP DATABASE IF EXISTS {DB_NAME} WITH (FORCE)'))


@pytest.fixture()
def client(alembic_db):
    """TestClient приложения, get_db переопределён на Alembic-мигрированную БД."""
    from fastapi.testclient import TestClient

    from app.db import get_db
    from app.main import app

    TestSession = sessionmaker(bind=alembic_db, autocommit=False, autoflush=False, class_=Session)

    def _override():
        session = TestSession()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.pop(get_db, None)


def _register(client, email: str) -> dict:
    resp = client.post(
        '/api/v1/auth/register',
        json={
            'company_name': f'Компания {uuid.uuid4().hex[:6]}',
            'email': email,
            'password': 'Passw0rd!123',
            'first_name': 'Тест',
            'last_name': 'Пользователь',
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


# ------------------------- Регистрация / вход / refresh -------------------------


def test_register_against_alembic_schema(client):
    data = _register(client, 'reg-enum@example.com')
    assert data['user']['role'] == 'company_admin'


def test_login_and_refresh_against_alembic_schema(client):
    _register(client, 'login-enum@example.com')

    login = client.post(
        '/api/v1/auth/login',
        json={'email': 'login-enum@example.com', 'password': 'Passw0rd!123'},
    )
    assert login.status_code == 200, login.text
    body = login.json()
    assert body['user']['role'] == 'company_admin'

    refresh = client.post('/api/v1/auth/refresh', json={'refresh_token': body['tokens']['refresh_token']})
    assert refresh.status_code == 200, refresh.text
    assert refresh.json()['tokens']['access_token']


# ------------------------- Все четыре роли -------------------------


def test_all_four_roles_roundtrip(client, alembic_db):
    """Каждая роль пишется и читается через ORM против Alembic-enum; в БД — значения."""
    from app.models.company import Company
    from app.models.enums import UserRole
    from app.models.user import User
    from app.security.password import hash_password

    Sess = sessionmaker(bind=alembic_db)
    with Sess() as s:
        company = Company(id=uuid.uuid4(), name='Роли', slug=f'roles-{uuid.uuid4().hex[:6]}', is_active=True)
        s.add(company)
        s.flush()
        emails = {}
        for role in (UserRole.SUPERADMIN, UserRole.COMPANY_ADMIN, UserRole.MANAGER, UserRole.USER):
            email = f'{role.value}@example.com'
            emails[role] = email
            s.add(
                User(
                    id=uuid.uuid4(),
                    company_id=company.id,
                    email=email,
                    password_hash=hash_password('Passw0rd!123'),
                    first_name='Роль',
                    last_name=role.value,
                    role=role,
                    is_active=True,
                    is_email_verified=True,
                )
            )
        s.commit()

        # В БД лежат нижнерегистровые ЗНАЧЕНИЯ, а не имена членов.
        raw = dict(s.execute(text('SELECT email, role::text FROM users WHERE email LIKE :p'), {'p': '%@example.com'}).fetchall())
        for role, email in emails.items():
            assert raw[email] == role.value

    # Логин под каждой ролью возвращает корректную строку роли.
    for role, email in emails.items():
        resp = client.post('/api/v1/auth/login', json={'email': email, 'password': 'Passw0rd!123'})
        assert resp.status_code == 200, f'{role}: {resp.text}'
        assert resp.json()['user']['role'] == role.value


def test_invalid_role_rejected_by_db(alembic_db):
    """Значение вне enum отвергается на уровне PostgreSQL."""
    with alembic_db.connect() as conn:
        with pytest.raises(DBAPIError):
            conn.execute(
                text(
                    "INSERT INTO users (id, company_id, email, password_hash, first_name, last_name, role, is_active, is_email_verified) "
                    "VALUES (:id, (SELECT id FROM companies LIMIT 1), 'bad-role@example.com', 'x', 'a', 'b', 'SUPER_DUPER_ADMIN', true, true)"
                ),
                {'id': str(uuid.uuid4())},
            )


# ------------------------- Миграционный цикл -------------------------


def test_alembic_downgrade_upgrade_cycle(alembic_db):
    """downgrade base → upgrade head проходит; повторный upgrade head — no-op (существующая БД)."""
    result = _alembic('downgrade', 'base')
    assert result.returncode == 0, result.stderr
    result = _alembic('upgrade', 'head')
    assert result.returncode == 0, result.stderr
    # «Существующая обновлённая БД»: повторный upgrade head не делает ничего и не падает.
    result = _alembic('upgrade', 'head')
    assert result.returncode == 0, result.stderr

    # Схема снова рабочая: enum на месте со значениями в нижнем регистре.
    with alembic_db.connect() as conn:
        values = [r[0] for r in conn.execute(text(
            "SELECT enumlabel FROM pg_enum e JOIN pg_type t ON t.oid = e.enumtypid WHERE t.typname = 'user_role_enum' ORDER BY e.enumsortorder"
        ))]
    assert values == ['superadmin', 'company_admin', 'manager', 'user']
