"""Общие фикстуры для интеграционных тестов модуля marking.

Использует отдельную тестовую БД (TEST_DATABASE_URL) и переопределяет зависимость
get_db на изолированную сессию. Схема создаётся через Base.metadata.create_all.
"""

from __future__ import annotations

import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

TEST_DATABASE_URL = os.environ.get(
    'TEST_DATABASE_URL', 'postgresql+psycopg2://postgres:postgres@127.0.0.1:5433/prostomark_test'
)

# Гарантируем безопасное окружение для тестов ДО импорта приложения.
os.environ.setdefault('CRPT_ENV', 'sandbox')
os.environ.setdefault('CRPT_ALLOW_PRODUCTION', 'false')
os.environ.setdefault('CRPT_DRY_RUN', 'true')
os.environ.setdefault('JWT_SECRET', 'testsecret')

from app.db import get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models.base import Base  # noqa: E402
from app.models.company import Company  # noqa: E402
from app.models.enums import UserRole  # noqa: E402
from app.models.user import User  # noqa: E402
from app.security.tokens import create_access_token  # noqa: E402

_engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False, class_=Session)


@pytest.fixture(scope='session', autouse=True)
def _schema():
    Base.metadata.drop_all(_engine)
    Base.metadata.create_all(_engine)
    yield
    Base.metadata.drop_all(_engine)


@pytest.fixture()
def db() -> Session:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(autouse=True)
def _clean_tables():
    """Чистим данные между тестами (порядок — с учётом FK)."""
    yield
    with _engine.begin() as conn:
        conn.execute(text('SET session_replication_role = replica'))
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(text(f'TRUNCATE TABLE "{table.name}" CASCADE'))
        conn.execute(text('SET session_replication_role = origin'))


@pytest.fixture()
def client() -> TestClient:
    def _override():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.pop(get_db, None)


# ----------------------------- Хелперы сидинга -----------------------------


def make_company(db: Session, name: str) -> Company:
    company = Company(id=uuid.uuid4(), name=name, slug=f'{name}-{uuid.uuid4().hex[:6]}', is_active=True)
    db.add(company)
    db.commit()
    return company


def make_user(db: Session, company: Company, role: UserRole, email: str | None = None) -> User:
    user = User(
        id=uuid.uuid4(),
        company_id=company.id,
        email=email or f'{role.value}-{uuid.uuid4().hex[:8]}@example.com',
        password_hash='x',
        first_name='Test',
        last_name=role.value,
        role=role,
        is_active=True,
        is_email_verified=True,
    )
    db.add(user)
    db.commit()
    return user


def auth_headers(user: User) -> dict:
    token = create_access_token(str(user.id), str(user.role), str(user.company_id))
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture()
def seed(db: Session):
    """Две компании; в компании A — все роли."""
    company_a = make_company(db, 'CompanyA')
    company_b = make_company(db, 'CompanyB')
    users = {
        'superadmin': make_user(db, company_a, UserRole.SUPERADMIN),
        'company_admin': make_user(db, company_a, UserRole.COMPANY_ADMIN),
        'manager': make_user(db, company_a, UserRole.MANAGER),
        'user': make_user(db, company_a, UserRole.USER),
    }
    user_b = make_user(db, company_b, UserRole.COMPANY_ADMIN)
    return {
        'company_a': company_a,
        'company_b': company_b,
        'users': users,
        'user_b': user_b,
    }
