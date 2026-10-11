"""Create ONLY synthetic browser-test data in a dedicated *_test database."""

import os
from urllib.parse import urlsplit

if not urlsplit(os.environ.get("DATABASE_URL", "")).path.endswith("_test"):
    raise SystemExit("Use a dedicated database whose name ends in _test")
from app.db import SessionLocal
from app.models.company import Company
from app.models.user import User
from app.models.product import Product
from app.models.enums import UserRole
from app.security.password import hash_password

with SessionLocal() as db:
    company = Company(name="Тест продаж", slug="sales-browser-test", is_active=True)
    db.add(company)
    db.flush()
    user = User(
        company_id=company.id,
        email="sales-test@example.com",
        first_name="Анна",
        last_name="Тестовая",
        password_hash=hash_password("SalesTestOnly123!"),
        role=UserRole.COMPANY_ADMIN,
        is_active=True,
        is_email_verified=True,
    )
    db.add(user)
    db.flush()
    db.add(
        Product(
            company_id=company.id,
            name="Крем увлажняющий 50 мл",
            article="CREAM-50",
            gtin="04600000000001",
            created_by=user.id,
        )
    )
    db.commit()
print("Synthetic sales test account created")
