.PHONY: up down build logs lint local-install local-backend local-frontend

# Docker Commands (Default)
up:
	docker compose up --build

run:
	docker compose up

down:
	docker compose down

build:
	docker compose build
	docker compose up -d
	docker compose exec backend python manage.py migrate
	docker compose logs -f

migrate:
	docker compose exec backend python manage.py migrate

logs:
	docker compose logs -f

docker-lint:
	docker compose exec payroll-backend ruff check .
	docker compose exec payroll-frontend npm run lint

# Local Commands (Legacy)
local-install:
	cd payroll-backend && python3 -m venv venv && ./venv/bin/pip install -r requirements.txt
	cd payroll-frontend && npm install

local-backend:
	cd payroll-backend && ./venv/bin/python3 manage.py runserver 0.0.0.0:8000

local-frontend:
	cd payroll-frontend && npm run dev

lint:
	cd payroll-backend && ./venv/bin/ruff check .
	cd payroll-frontend && npm run lint
