"""Exercise sales upgrade/downgrade, preserving synthetic catalog/auth data.
Run only against a dedicated empty *_test database. Never use production.
"""

import os
from pathlib import Path
from urllib.parse import urlsplit
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, text, inspect

url = os.environ.get("DATABASE_URL", "")
if not urlsplit(url).path.endswith("_test"):
    raise SystemExit("Use a dedicated disposable *_test database")
backend = Path(__file__).resolve().parents[1] / "backend"
config = Config(str(backend / "alembic.ini"))
config.set_main_option("script_location", str(backend / "alembic"))
engine = create_engine(url)
if inspect(engine).has_table("users"):
    raise SystemExit("Migration check requires an empty test database")
command.upgrade(config, "20260716_0002")
with engine.begin() as db:
    db.execute(
        text(
            "INSERT INTO companies (id,name,slug,is_active) VALUES ('11111111-1111-1111-1111-111111111111','Synthetic','synthetic-migration',true)"
        )
    )
    db.execute(
        text(
            "INSERT INTO users (id,company_id,email,password_hash,first_name,last_name,role,is_active,is_email_verified) VALUES ('22222222-2222-2222-2222-222222222222','11111111-1111-1111-1111-111111111111','migration@example.com','test-only','Test','Test','company_admin',true,true)"
        )
    )
    db.execute(
        text(
            "INSERT INTO products (id,company_id,name,created_by) VALUES ('33333333-3333-3333-3333-333333333333','11111111-1111-1111-1111-111111111111','Крем','22222222-2222-2222-2222-222222222222')"
        )
    )
for target in ["head", "20260716_0002", "head"]:
    (command.upgrade if target == "head" else command.downgrade)(config, target)
    with engine.connect() as db:
        assert db.scalar(text("SELECT count(*) FROM products")) == 1
        assert db.scalar(text("SELECT count(*) FROM users")) == 1
    tables = inspect(engine).get_table_names()
    assert sum(t.startswith("sales_") for t in tables) == (8 if target == "head" else 0)
    if target == "head":
        with engine.connect() as db:
            assert db.scalar(text("SELECT count(*) FROM sales_document_templates")) == 3
        assert any(
            f["name"] == "sales_order_customer_tenant"
            for f in inspect(engine).get_foreign_keys("sales_orders")
        )
print("Sales migration upgrade/downgrade/upgrade OK; catalog and users preserved")
