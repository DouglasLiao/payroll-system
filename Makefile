.PHONY: up down build logs lint local-install local-backend local-frontend

# Docker Commands (Default)
up:
	docker compose up --build

down:
	docker compose down

build:
	docker compose build && docker compose up

logs:
	docker compose logs -f

docker-lint:
	docker compose exec backend ruff check .
	docker compose exec frontend npm run lint

# Local Commands (Legacy)
local-install:
	cd backend && python3 -m venv venv && ./venv/bin/pip install -r requirements.txt
	cd frontend && npm install

local-backend:
	cd backend && ./venv/bin/python3 manage.py runserver 0.0.0.0:8000

local-frontend:
	cd frontend && npm run dev

lint:
	cd backend && ./venv/bin/ruff check .
	cd frontend && npm run lint
