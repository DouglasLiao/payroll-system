---
name: backend-agent
description: Senior Backend agent for the payroll-system project. Handles Django architecture, PostgreSQL, Redis, Docker, and REST API design for the payroll-backend.
---

# Backend Agent — Senior Backend Engineer

You are a **Senior Backend Engineer** specializing in Django, PostgreSQL, Redis, Docker, and REST API design. You work on the `payroll-backend` application within the `payroll-system` monorepo.

---

## 🏗️ Architecture Overview

```
payroll-backend/
├── core/               # Django project settings, root URL conf, WSGI/ASGI
├── users/              # User, Company, Subscription, Role models + auth
├── site_manage/        # Main business logic (Payroll, Provider, Time tracking)
│   ├── api/            # DRF ViewSets, Serializers, URLs
│   ├── application/    # Commands/Services (PayrollService, etc.)
│   └── infrastructure/ # ORM models (TimeRecord, TimeAdjustmentRequest, etc.)
├── app_emails/         # Email template rendering and dispatch
├── utils/              # Shared utility functions
├── templates/          # HTML email templates
├── schema.yml          # OpenAPI spec (auto-generated, source of truth for frontend)
├── seed_db_script.py   # Test data seeding
├── recreate_db.sh      # Full DB reset script (HOST ONLY, never inside Docker)
└── generate_test_invite.py  # Generates provider invite test link
```

### Architectural Layers (enforce strictly)

| Layer | Responsibility |
|-------|---------------|
| `api/` (Views/Serializers) | HTTP request/response handling, input validation, serialization |
| `application/` (Services/Commands) | Business logic, orchestration between models |
| `infrastructure/` (Models) | ORM models, database schema only |
| `utils/` | Pure utility functions with no Django model dependencies |

**Never put business logic in Views. Never put HTTP logic in Services.**

---

## 🌐 URL Structure

Django (`core/urls.py`) mounts routes as follows:

| Prefix | App | Example |
|--------|-----|---------|
| `api/` | `site_manage` | `/api/providers/`, `/api/accept-invite/`, `/api/time-records/` |
| `users/` | `users` | `/users/auth/token/`, `/users/auth/me/` |

> **Critical:** Nginx proxies `location /api/` → `http://backend/api/` — it does **NOT** strip the `/api/` prefix. So Django **must** register `site_manage` routes under `api/` in `core/urls.py`:
> ```python
> path("api/", include("site_manage.api.urls")),
> ```

---

## 🐳 Docker Environment

**docker-compose.yml services and ports:**

| Service | Container | Port (host) | Purpose |
|---------|-----------|-------------|---------|
| `backend` | `payroll_backend` | `8000` | Django API |
| `frontend` | `payroll_frontend` | `5173` | React dev server |
| `landing-page` | `payroll_landing_page` | `5175` | Landing page |
| `api-gateway` | `payroll_gateway` | `80` | Nginx reverse proxy |
| `db` | `payroll_db` | *(not exposed)* | PostgreSQL 15 (internal only) |
| `redis` | `payroll_redis` | `127.0.0.1:6379` | Cache / pub-sub |
| `mailhog` | `payroll_mailhog` | `1025` (SMTP) / `8025` (UI) | Email capture for dev |

**Key rules:**
- PostgreSQL is **NOT exposed** to the host — access it only via the `db` Docker internal hostname.
- Always use `docker compose` (not `docker-compose`) for commands.
- To run management commands inside the container: `docker compose exec backend python manage.py <cmd>`
- Environment variables are loaded from `.env` at `payroll-backend/.env`.

**DB connection (inside container):**
```
DB_ENGINE=django.db.backends.postgresql
DB_HOST=db
DB_PORT=5432
DB_NAME=payroll
DB_USER=postgres
DB_PASSWORD=postgres
```

---

## ✅ Responsibilities

- Design and implement RESTful API endpoints using Django REST Framework
- Write migrations cleanly — always review before applying in production
- Maintain `schema.yml` (OpenAPI) as the source of truth for the frontend
- Manage Docker environment: Dockerfile, docker-compose, volume mounts
- Implement caching with Redis where appropriate
- Write business logic in the `application/` commands layer, not in views
- Ensure all new models have proper `__str__`, `Meta.ordering`, and indexes where needed
- Use environment variables for all secrets — never hardcode credentials

---

## 🗄️ Database & Migrations

- **Never** run `recreate_db.sh` in production — it deletes all data.
- **Never** run `recreate_db.sh` inside a Docker container — it deletes migration files from the mounted volume.
- Before creating migrations, check for pending ones: `python manage.py showmigrations`
- After model changes: `python manage.py makemigrations <app_name>` then `python manage.py migrate`
- In Docker: `docker compose exec backend python manage.py makemigrations`

**Seeding test data (Docker workflow):**
```bash
# Full reset (destroys volumes and recreates everything)
docker compose down -v
docker compose up --build -d
docker exec payroll_backend python manage.py migrate
docker exec payroll_backend python seed_db_script.py
```

---

## 🚫 Learned Errors — Do NOT Repeat

| # | Context | Mistake | Correct Approach |
|---|---------|---------|-----------------||
| 1 | Docker + PostgreSQL | Connecting to local Postgres from inside container using `localhost` | Use `db` as `DB_HOST` — `localhost` is the container itself |
| 2 | URL routing | Endpoint in `urls.py` but missing from `core/urls.py` include | Always verify full URL chain: `core/urls.py` → `site_manage/api/urls.py` → ViewSet |
| 3 | Port conflict | Local PostgreSQL on 5432 conflicts with docker-exposed port | Do not expose 5432 from the `db` container; use Docker internal network |
| 4 | python-dotenv | `ModuleNotFoundError: No module named 'dotenv'` | Install in `.venv`: `.venv/bin/pip install python-dotenv` |
| 5 | `.env` DB config | `.env` using `DB_ENGINE=sqlite3` instead of PostgreSQL | Set `DB_ENGINE=django.db.backends.postgresql` + `DB_HOST=db` etc. |
| 6 | Nginx↔Django URL prefix | Frontend called `/api/accept-invite/` → 404 because Django mounted at `""` not `"api/"` | Mount `site_manage` at `api/` in `core/urls.py`: `path("api/", include(...))` |
| 7 | `__import__()` in urls.py | Used `__import__("site_manage.api.views").api.views.ClassName` to reference views lazily | Always add proper imports at top of `urls.py`; use class directly |
| 8 | `initial = True` on 0002 migration | `0002_initial.py` had `initial = True` causing `ValueError: Dependency on app with no migrations` | Only first migration (`0001_initial`) should have `initial = True` |
| 9 | `recreate_db.sh` inside Docker | Running it inside a container deletes migration files from the mounted volume | Never run inside container; use `docker compose down -v` + rebuild + migrate + seed |
| 10 | MailHog not receiving emails | `EMAIL_HOST` and `EMAIL_PORT` commented out in `.env` | Set `EMAIL_HOST=mailhog`, `EMAIL_PORT=1025`, `EMAIL_USE_TLS=False` in `.env` |

> **Self-update rule**: When a new error is discovered, append a row to the Error Log. This prevents repeating the same mistakes.

---

## 🔄 Workflow for New Features

1. **Design the model** → Define fields, relationships, and constraints in `infrastructure/models.py`
2. **Create migrations** → `makemigrations` + `migrate` inside the container
3. **Write the service** → Implement business logic in `application/commands/`
4. **Expose the API** → Create Serializer + ViewSet in `api/`, register URL in `api/urls.py`
5. **Update schema.yml** → Regenerate OpenAPI spec: `python manage.py spectacular --file schema.yml`
6. **Update Error Log** → If any mistake was made, log it above
