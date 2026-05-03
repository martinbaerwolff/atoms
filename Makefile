.DEFAULT_GOAL := help
SHELL := /bin/bash

# Auto-load .env if present (so DATABASE_URL etc. are available in host shells)
ifneq (,$(wildcard .env))
include .env
export
endif

.PHONY: help install install-backend install-frontend dev dev-backend dev-frontend \
        down logs ps psql migrate makemigration fresh \
        test test-backend test-frontend test-e2e \
        lint lint-backend lint-frontend format format-backend format-frontend \
        typecheck check pre-commit-install ci-local

help:
	@printf "Atoms — common targets\n\n"
	@awk 'BEGIN{FS=":.*##"} /^[a-zA-Z0-9_-]+:.*##/ {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# --- setup -----------------------------------------------------------

install: install-backend install-frontend pre-commit-install ## Install all deps (backend + frontend + pre-commit)

install-backend: ## uv sync the backend
	cd backend && uv sync --all-extras

install-frontend: ## npm install the frontend
	cd frontend && npm install

pre-commit-install: ## install pre-commit hooks into local git
	uv tool run --from pre-commit pre-commit install || pre-commit install

# --- dev -------------------------------------------------------------

dev: ## Start full stack via docker compose (postgres + backend + frontend)
	docker compose up --build

dev-backend: ## Run backend natively (requires postgres running)
	cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Run frontend natively
	cd frontend && npm run dev -- --host

down: ## Stop and remove docker compose stack
	docker compose down

logs: ## Tail compose logs
	docker compose logs -f --tail=100

ps: ## Show compose status
	docker compose ps

psql: ## Open psql in compose db
	docker compose exec db psql -U $${POSTGRES_USER:-atoms} -d $${POSTGRES_DB:-atoms}

# --- db / migrations -------------------------------------------------

migrate: ## Apply alembic migrations against compose db
	docker compose run --rm backend uv run alembic upgrade head

makemigration: ## Autogenerate alembic migration: make makemigration name=add_atoms
	docker compose run --rm backend uv run alembic revision --autogenerate -m "$(name)"

fresh: ## Drop volumes, recreate db, run migrations (DESTRUCTIVE)
	docker compose down -v
	docker compose up -d db
	@sleep 3
	$(MAKE) migrate

# --- test ------------------------------------------------------------

test: test-backend test-frontend ## Run all tests (backend + frontend unit). E2E via test-e2e.

test-backend: ## pytest in the backend (includes dev extras: testcontainers etc.)
	cd backend && uv sync --extra dev -q && uv run pytest

test-frontend: ## vitest in the frontend
	cd frontend && npm run test:unit

test-e2e: ## playwright e2e (requires services running)
	cd frontend && npm run test:e2e

# --- lint / format / typecheck ---------------------------------------

lint: lint-backend lint-frontend ## Lint everything (no autofix)

lint-backend:
	cd backend && uv run ruff check . && uv run ruff format --check .

lint-frontend:
	cd frontend && npm run lint && npm run check

format: format-backend format-frontend ## Format everything (autofix)

format-backend:
	cd backend && uv run ruff check --fix . && uv run ruff format .

format-frontend:
	cd frontend && npm run format

typecheck: ## mypy + svelte-check
	cd backend && uv run mypy .
	cd frontend && npm run check

check: lint typecheck test ## Local equivalent of CI

ci-local: ## Same as check but also build the frontend
	$(MAKE) check
	cd frontend && npm run build
