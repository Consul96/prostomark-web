# ProstoMark Web

Production-oriented SaaS platform for product marking workflows: auth, multi-tenant data isolation, documents + AI processing, calculations, analytics, subscriptions, and admin management.

## Stack

- Backend: Python 3.11, FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL, Redis, Celery
- Frontend: React, TypeScript, Vite, TailwindCSS, React Router, React Query, Zustand
- Infra: Docker, Docker Compose, Nginx, GitHub Actions
- Integrations: Stripe, OpenAI API, SMTP

## Project Structure

```text
prostomark-web/
  backend/
    app/
      main.py
      config.py
      db.py
      dependencies.py
      models/
      schemas/
      crud/
      services/
      security/
      routers/
      tasks/
      utils/
    alembic/
      versions/
    tests/
    requirements.txt
    Dockerfile
    Dockerfile.worker
    alembic.ini
  frontend/
    src/
      app/
      pages/
      widgets/
      features/
      entities/
      shared/
      components/
      hooks/
      api/
      store/
      layouts/
      styles/
    package.json
    Dockerfile
  infra/
    nginx/
      default.conf
    github/
      workflows/
        ci.yml
  .github/
    workflows/
      ci.yml
  docker-compose.yml
  .env.example
  README.md
```

## Core Functional Blocks

- Public pages: `/`, `/pricing`, `/faq`, `/login`, `/register`
- App pages: `/app/dashboard`, `/app/calculator`, `/app/products`, `/app/documents`, `/app/history`, `/app/settings`
- Admin pages: `/admin`, `/admin/users`, `/admin/companies`, `/admin/subscriptions`, `/admin/logs`
- Multi-tenant scope: all tenant entities filtered by `company_id`; `superadmin` can access all records
- Auth: access + refresh JWT, token rotation, logout revocation
- Billing: Stripe checkout + webhook status sync
- Documents: file upload to local storage + async AI processing in Celery worker
- Audit: key actions written to `audit_logs`

## API (Backend)

Base prefix: `/api/v1`

- Auth:
  - `POST /auth/register`
  - `POST /auth/login`
  - `POST /auth/refresh`
  - `POST /auth/logout`
  - `GET /auth/me`
- Products:
  - `GET /products`
  - `POST /products`
  - `GET /products/{id}`
  - `PUT /products/{id}`
  - `DELETE /products/{id}`
- Documents:
  - `POST /documents/upload`
  - `GET /documents`
  - `GET /documents/{id}`
  - `DELETE /documents/{id}`
- Calculations:
  - `POST /calculations`
  - `GET /calculations`
  - `GET /calculations/{id}`
- Dashboard:
  - `GET /dashboard/summary`
- Admin:
  - `GET /admin/users`
  - `POST /admin/users`
  - `GET /admin/companies`
  - `GET /admin/subscriptions`
  - `GET /admin/logs`
- Billing:
  - `POST /billing/checkout`
  - `POST /billing/webhook`
  - `GET /billing/current-plan`

## Local Run (Docker)

1. Copy env file:

```bash
cp .env.example .env
```

2. Start services:

```bash
docker compose up --build
```

3. Open app:

- Frontend via Nginx: `http://localhost`
- API docs: `http://localhost/api/v1/docs`

## Local Run (Without Docker)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Worker

```bash
cd backend
celery -A app.tasks.celery_app.celery_app worker -l info -Q documents
```

### Frontend

```bash
cd frontend
npm ci
npm run dev
```

## Environment Variables

See `.env.example` for the full list:

- `DATABASE_URL`
- `JWT_SECRET`
- `REDIS_URL`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `OPENAI_API_KEY`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASS`
- `SMTP_FROM`

## CI

Workflow file:

- `infra/github/workflows/ci.yml`
- `.github/workflows/ci.yml`

Pipeline stages:

- install
- lint
- test
- docker build
