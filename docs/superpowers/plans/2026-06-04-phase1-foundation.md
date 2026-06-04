# Atoms Phase 1 — Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a fully working vertical slice — Docker infra, PostgreSQL schema, FastAPI CRUD API, and SvelteKit list/panel UI for all four atom types.

**Architecture:** Single-user SPA. FastAPI + PostgreSQL backend (sync SQLAlchemy, psycopg2). SvelteKit frontend (Svelte 5 runes, no SSR). Dev and Prod run in separate Docker Compose stacks with separate databases. All data persists in named Docker volumes. Daily backup via pg_dump to `./backups/`.

**Tech Stack:** Python 3.13, FastAPI 0.115, SQLAlchemy 2 (sync), Alembic, uv, pytest, psycopg2-binary, PostgreSQL 16, SvelteKit 2, Svelte 5 (runes), TypeScript, Vite, Docker Compose

---

## File Map

```
atoms/
├── docker-compose.yml          # Dev stack
├── docker-compose.prod.yml     # Prod stack
├── Makefile
├── .env.example
├── .gitignore
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   │       └── 001_initial_schema.py
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI app + router registration
│   │   ├── settings.py         # Pydantic settings from env
│   │   ├── db.py               # Engine + SessionLocal
│   │   ├── deps.py             # get_db dependency
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py         # Base, UUIDPrimaryKeyMixin, TimestampMixin
│   │   │   ├── person.py
│   │   │   ├── project.py
│   │   │   └── atom.py         # Atom + 3 association tables
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── person.py
│   │   │   ├── project.py
│   │   │   └── atom.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── persons.py
│   │   │   ├── projects.py
│   │   │   └── atoms.py
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── persons.py
│   │       ├── projects.py
│   │       └── atoms.py
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_persons.py
│       ├── test_projects.py
│       └── test_atoms.py
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── svelte.config.js
    ├── vite.config.ts
    ├── tsconfig.json
    └── src/
        ├── app.html
        ├── app.css
        ├── lib/
        │   ├── api/
        │   │   ├── types.ts
        │   │   ├── client.ts
        │   │   ├── atoms.ts
        │   │   ├── persons.ts
        │   │   └── projects.ts
        │   └── components/
        │       ├── TypeIcon.svelte
        │       ├── PersonAvatar.svelte
        │       ├── ProjectBadge.svelte
        │       ├── FilterBadges.svelte
        │       ├── AtomRow.svelte
        │       └── AtomPanel.svelte
        └── routes/
            ├── +layout.svelte
            └── +page.svelte
```

---

## Task 1: Project Scaffold

**Files:**
- Create: `docker-compose.yml`
- Create: `docker-compose.prod.yml`
- Create: `Makefile`
- Create: `.env.example`

- [ ] **Step 1: Create `.env.example`**

```bash
DB_PASSWORD=changeme
VITE_API_URL=http://localhost:8000
```

- [ ] **Step 2: Create `docker-compose.yml` (dev)**

```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: atoms_dev
      POSTGRES_USER: atoms
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - db_dev_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U atoms -d atoms_dev"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      target: dev
    environment:
      DATABASE_URL: postgresql://atoms:${DB_PASSWORD}@db:5432/atoms_dev
      ENV: development
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    command: uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

  frontend:
    build:
      context: ./frontend
      target: dev
    environment:
      VITE_API_URL: http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "5173:5173"
    depends_on:
      - backend

volumes:
  db_dev_data:
```

- [ ] **Step 3: Create `docker-compose.prod.yml`**

```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: atoms_prod
      POSTGRES_USER: atoms
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - db_prod_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U atoms -d atoms_prod"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      target: prod
    environment:
      DATABASE_URL: postgresql://atoms:${DB_PASSWORD}@db:5432/atoms_prod
      ENV: production
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      target: prod
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  db_prod_data:
```

- [ ] **Step 4: Create `Makefile`**

```makefile
.PHONY: dev start stop stop-prod logs test migrate backup

dev:
	cp -n .env.example .env 2>/dev/null || true
	docker compose up --build

start:
	cp -n .env.example .env 2>/dev/null || true
	docker compose -f docker-compose.prod.yml up --build -d

stop:
	docker compose down

stop-prod:
	docker compose -f docker-compose.prod.yml down

logs:
	docker compose logs -f

test:
	docker compose exec backend uv run pytest -v

migrate:
	docker compose exec backend uv run alembic upgrade head

backup:
	mkdir -p backups
	docker compose exec db pg_dump -U atoms atoms_dev > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "Backup saved to backups/"
```

- [ ] **Step 5: Commit**

```bash
git add docker-compose.yml docker-compose.prod.yml Makefile .env.example
git commit -m "feat: add docker-compose, Makefile, env scaffold"
```

---

## Task 2: Backend Scaffold

**Files:**
- Create: `backend/Dockerfile`
- Create: `backend/pyproject.toml`
- Create: `backend/alembic.ini`
- Create: `backend/app/__init__.py`
- Create: `backend/app/settings.py`
- Create: `backend/app/db.py`
- Create: `backend/app/deps.py`
- Create: `backend/app/main.py`

- [ ] **Step 1: Create `backend/Dockerfile`**

```dockerfile
FROM python:3.13-slim AS base
WORKDIR /app
RUN pip install uv

FROM base AS dev
COPY pyproject.toml .
RUN uv sync
COPY . .

FROM base AS prod
COPY pyproject.toml .
RUN uv sync --no-dev
COPY . .
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 2: Create `backend/pyproject.toml`**

```toml
[project]
name = "atoms-backend"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
    "sqlalchemy>=2.0",
    "psycopg2-binary>=2.9",
    "alembic>=1.14",
    "pydantic>=2.9",
    "pydantic-settings>=2.6",
]

[tool.uv]
dev-dependencies = [
    "pytest>=8",
    "httpx>=0.27",
    "pytest-env>=1.1",
]

[tool.pytest.ini_options]
env = [
    "DATABASE_URL=postgresql://atoms:changeme@localhost:5432/atoms_test",
]
```

- [ ] **Step 3: Create `backend/alembic.ini`**

```ini
[alembic]
script_location = alembic
prepend_sys_path = .
sqlalchemy.url = %(DATABASE_URL)s

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

- [ ] **Step 4: Create `backend/app/settings.py`**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    env: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()
```

- [ ] **Step 5: Create `backend/app/db.py`**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.settings import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
```

- [ ] **Step 6: Create `backend/app/deps.py`**

```python
from collections.abc import Generator
from sqlalchemy.orm import Session
from app.db import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 7: Create `backend/app/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Atoms API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:80"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
```

- [ ] **Step 8: Create empty `backend/app/__init__.py`** (empty file)

- [ ] **Step 9: Commit**

```bash
git add backend/
git commit -m "feat: backend scaffold — FastAPI, settings, db, deps"
```

---

## Task 3: Frontend Scaffold

**Files:**
- Create: `frontend/Dockerfile`
- Create: `frontend/package.json`
- Create: `frontend/svelte.config.js`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/src/app.html`
- Create: `frontend/src/app.css`
- Create: `frontend/src/routes/+layout.svelte`
- Create: `frontend/src/routes/+page.svelte` (stub)

- [ ] **Step 1: Create `frontend/Dockerfile`**

```dockerfile
FROM node:22-alpine AS base
WORKDIR /app
COPY package*.json .

FROM base AS dev
RUN npm install
COPY . .
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

FROM base AS builder
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine AS prod
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

- [ ] **Step 2: Create `frontend/nginx.conf`**

```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    location /api/ {
        proxy_pass http://backend:8000/;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

- [ ] **Step 3: Create `frontend/package.json`**

```json
{
  "name": "atoms-frontend",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite dev",
    "build": "vite build",
    "preview": "vite preview",
    "check": "svelte-kit sync && svelte-check --tsconfig ./tsconfig.json"
  },
  "devDependencies": {
    "@sveltejs/adapter-static": "^3.0.0",
    "@sveltejs/kit": "^2.0.0",
    "@sveltejs/vite-plugin-svelte": "^4.0.0",
    "svelte": "^5.0.0",
    "svelte-check": "^4.0.0",
    "typescript": "^5.0.0",
    "vite": "^6.0.0"
  }
}
```

- [ ] **Step 4: Run `npm install` inside frontend**

```bash
docker compose run --rm frontend npm install
```

Expected: `node_modules/` created, `package-lock.json` updated.

- [ ] **Step 5: Create `frontend/svelte.config.js`**

```js
import adapter from '@sveltejs/adapter-static'

export default {
  kit: {
    adapter: adapter({ fallback: 'index.html' }),
  },
}
```

- [ ] **Step 6: Create `frontend/vite.config.ts`**

```typescript
import { sveltekit } from '@sveltejs/kit/vite'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [sveltekit()],
  server: {
    proxy: {
      '/api': { target: 'http://backend:8000', rewrite: (p) => p.replace(/^\/api/, '') },
    },
  },
})
```

- [ ] **Step 7: Create `frontend/tsconfig.json`**

```json
{
  "extends": "./.svelte-kit/tsconfig.json",
  "compilerOptions": {
    "strict": true
  }
}
```

- [ ] **Step 8: Create `frontend/src/app.html`**

```html
<!doctype html>
<html lang="de">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%sveltekit.assets%/favicon.png" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    %sveltekit.head%
  </head>
  <body data-sveltekit-preload-data="hover">
    <div style="display: contents">%sveltekit.body%</div>
  </body>
</html>
```

- [ ] **Step 9: Create `frontend/src/app.css`**

```css
*, *::before, *::after { box-sizing: border-box; }

:root {
  --accent: #10B981;
  --accent-light: #D1FAE5;
  --text: #111827;
  --text-muted: #6B7280;
  --border: #E5E7EB;
  --bg: #FFFFFF;
  --bg-hover: #F9FAFB;
  --font: 'Inter', system-ui, sans-serif;
}

body {
  margin: 0;
  font-family: var(--font);
  color: var(--text);
  background: var(--bg);
  font-size: 14px;
  line-height: 1.5;
}

button { cursor: pointer; font-family: inherit; }
input, textarea, select { font-family: inherit; }
```

- [ ] **Step 10: Create `frontend/src/routes/+layout.svelte`**

```svelte
<script lang="ts">
  import '../app.css'
  let { children } = $props()
</script>

{@render children()}
```

- [ ] **Step 11: Create stub `frontend/src/routes/+page.svelte`**

```svelte
<script lang="ts">
</script>

<main>
  <h1>Atoms</h1>
  <p>Loading...</p>
</main>
```

- [ ] **Step 12: Verify dev stack starts**

```bash
make dev
```

Expected: `http://localhost:5173` shows "Atoms / Loading...", `http://localhost:8000/health` returns `{"status":"ok"}`.

- [ ] **Step 13: Commit**

```bash
git add frontend/
git commit -m "feat: frontend scaffold — SvelteKit, Svelte 5, static adapter"
```

---

## Task 4: DB Models

**Files:**
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/base.py`
- Create: `backend/app/models/person.py`
- Create: `backend/app/models/project.py`
- Create: `backend/app/models/atom.py`

- [ ] **Step 1: Create `backend/app/models/base.py`**

```python
import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class UUIDPrimaryKeyMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
```

- [ ] **Step 2: Create `backend/app/models/person.py`**

```python
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Person(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "persons"

    name: Mapped[str] = mapped_column(Text, nullable=False)
    photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    organizations: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, default=list, server_default="{}"
    )
```

- [ ] **Step 3: Create `backend/app/models/project.py`**

```python
from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Project(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(Text, nullable=False)
    color: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon: Mapped[str | None] = mapped_column(Text, nullable=True)
```

- [ ] **Step 4: Create `backend/app/models/atom.py`**

```python
from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Table, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.person import Person
    from app.models.project import Project

atom_responsible = Table(
    "atom_responsible",
    Base.metadata,
    Column("atom_id", UUID(as_uuid=True), ForeignKey("atoms.id", ondelete="CASCADE"), primary_key=True),
    Column("person_id", UUID(as_uuid=True), ForeignKey("persons.id", ondelete="CASCADE"), primary_key=True),
)

atom_participants = Table(
    "atom_participants",
    Base.metadata,
    Column("atom_id", UUID(as_uuid=True), ForeignKey("atoms.id", ondelete="CASCADE"), primary_key=True),
    Column("person_id", UUID(as_uuid=True), ForeignKey("persons.id", ondelete="CASCADE"), primary_key=True),
)

atom_projects = Table(
    "atom_projects",
    Base.metadata,
    Column("atom_id", UUID(as_uuid=True), ForeignKey("atoms.id", ondelete="CASCADE"), primary_key=True),
    Column("project_id", UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
)


class Atom(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "atoms"

    title: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    type: Mapped[str] = mapped_column(Text, nullable=False)
    captured: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[str | None] = mapped_column(Text, nullable=True)
    complexity: Mapped[str | None] = mapped_column(Text, nullable=True)
    deadline_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    alarm_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    responsible: Mapped[list[Person]] = relationship(secondary=atom_responsible, lazy="select")
    participants: Mapped[list[Person]] = relationship(secondary=atom_participants, lazy="select")
    projects: Mapped[list[Project]] = relationship(secondary=atom_projects, lazy="select")
```

- [ ] **Step 5: Update `backend/app/models/__init__.py`** to expose all models for Alembic autodiscovery

```python
from app.models.atom import Atom
from app.models.base import Base
from app.models.person import Person
from app.models.project import Project

__all__ = ["Base", "Person", "Project", "Atom"]
```

- [ ] **Step 6: Commit**

```bash
git add backend/app/models/
git commit -m "feat: SQLAlchemy models — Person, Project, Atom with M2M relations"
```

---

## Task 5: Alembic Migration

**Files:**
- Create: `backend/alembic/env.py`
- Create: `backend/alembic/versions/001_initial_schema.py`

- [ ] **Step 1: Create `backend/alembic/env.py`**

```python
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])

import app.models  # noqa: F401 — ensures all models are registered
from app.models.base import Base

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

- [ ] **Step 2: Generate migration**

```bash
docker compose exec backend uv run alembic revision --autogenerate -m "initial_schema"
```

Expected: a new file appears in `alembic/versions/` with `001_...` prefix. Review it — it should create tables: `persons`, `projects`, `atoms`, `atom_responsible`, `atom_participants`, `atom_projects`.

- [ ] **Step 3: Run migration**

```bash
make migrate
```

Expected: `INFO  [alembic.runtime.migration] Running upgrade  -> <rev>, initial_schema`

- [ ] **Step 4: Verify tables exist**

```bash
docker compose exec db psql -U atoms -d atoms_dev -c "\dt"
```

Expected: lists all 6 tables.

- [ ] **Step 5: Commit**

```bash
git add backend/alembic/
git commit -m "feat: Alembic setup + initial schema migration"
```

---

## Task 6: Test Infrastructure

**Files:**
- Create: `backend/tests/__init__.py` (empty)
- Create: `backend/tests/conftest.py`

- [ ] **Step 1: Create test database**

```bash
docker compose exec db psql -U atoms -c "CREATE DATABASE atoms_test;"
```

Expected: `CREATE DATABASE`

- [ ] **Step 2: Create `backend/tests/conftest.py`**

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.deps import get_db
from app.main import app
from app.models.base import Base

TEST_DATABASE_URL = "postgresql://atoms:changeme@db:5432/atoms_test"

engine = create_engine(TEST_DATABASE_URL)


@pytest.fixture(scope="session", autouse=True)
def setup_schema():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

- [ ] **Step 3: Run tests to verify infrastructure works**

```bash
make test
```

Expected: `0 passed` (no tests yet) with no errors. If DB connection fails, check `TEST_DATABASE_URL` matches the running db service.

- [ ] **Step 4: Commit**

```bash
git add backend/tests/
git commit -m "feat: test infrastructure — conftest with real DB, rollback per test"
```

---

## Task 7: Person CRUD (TDD)

**Files:**
- Create: `backend/app/schemas/person.py`
- Create: `backend/app/services/persons.py`
- Create: `backend/app/routers/persons.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_persons.py`

- [ ] **Step 1: Write failing tests — `backend/tests/test_persons.py`**

```python
import uuid


def test_create_person(client):
    resp = client.post("/persons/", json={"name": "Anna Müller"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Anna Müller"
    assert data["organizations"] == []
    assert data["photo_url"] is None
    assert "id" in data


def test_create_person_with_org(client):
    resp = client.post("/persons/", json={"name": "Bob", "organizations": ["Platomo", "TUD"]})
    assert resp.status_code == 201
    assert resp.json()["organizations"] == ["Platomo", "TUD"]


def test_list_persons(client):
    client.post("/persons/", json={"name": "Anna"})
    client.post("/persons/", json={"name": "Bob"})
    resp = client.get("/persons/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_get_person(client):
    created = client.post("/persons/", json={"name": "Anna"}).json()
    resp = client.get(f"/persons/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Anna"


def test_update_person(client):
    created = client.post("/persons/", json={"name": "Anna"}).json()
    resp = client.patch(f"/persons/{created['id']}", json={"name": "Anna M.", "organizations": ["Platomo"]})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Anna M."
    assert resp.json()["organizations"] == ["Platomo"]


def test_delete_person(client):
    created = client.post("/persons/", json={"name": "Anna"}).json()
    del_resp = client.delete(f"/persons/{created['id']}")
    assert del_resp.status_code == 204
    get_resp = client.get(f"/persons/{created['id']}")
    assert get_resp.status_code == 404


def test_get_nonexistent_person(client):
    resp = client.get(f"/persons/{uuid.uuid4()}")
    assert resp.status_code == 404


def test_deleted_persons_excluded_from_list(client):
    created = client.post("/persons/", json={"name": "Anna"}).json()
    client.delete(f"/persons/{created['id']}")
    resp = client.get("/persons/")
    assert all(p["id"] != created["id"] for p in resp.json())
```

- [ ] **Step 2: Run tests — verify they all fail**

```bash
make test
```

Expected: `ImportError` or `404` errors — no routes exist yet.

- [ ] **Step 3: Create `backend/app/schemas/__init__.py`** (empty)

- [ ] **Step 4: Create `backend/app/schemas/person.py`**

```python
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PersonCreate(BaseModel):
    name: str
    photo_url: str | None = None
    organizations: list[str] = []


class PersonUpdate(BaseModel):
    name: str | None = None
    photo_url: str | None = None
    organizations: list[str] | None = None


class PersonRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    photo_url: str | None
    organizations: list[str]
    created_at: datetime
    updated_at: datetime
```

- [ ] **Step 5: Create `backend/app/services/__init__.py`** (empty)

- [ ] **Step 6: Create `backend/app/services/persons.py`**

```python
import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.person import Person
from app.schemas.person import PersonCreate, PersonUpdate


def list_persons(db: Session) -> list[Person]:
    return db.query(Person).filter(Person.deleted_at.is_(None)).all()


def get_person(db: Session, person_id: uuid.UUID) -> Person | None:
    return (
        db.query(Person)
        .filter(Person.id == person_id, Person.deleted_at.is_(None))
        .first()
    )


def create_person(db: Session, data: PersonCreate) -> Person:
    person = Person(**data.model_dump())
    db.add(person)
    db.commit()
    db.refresh(person)
    return person


def update_person(db: Session, person: Person, data: PersonUpdate) -> Person:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(person, field, value)
    db.commit()
    db.refresh(person)
    return person


def delete_person(db: Session, person: Person) -> None:
    person.deleted_at = datetime.now(UTC)
    db.commit()
```

- [ ] **Step 7: Create `backend/app/routers/__init__.py`** (empty)

- [ ] **Step 8: Create `backend/app/routers/persons.py`**

```python
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import app.services.persons as svc
from app.deps import get_db
from app.schemas.person import PersonCreate, PersonRead, PersonUpdate

router = APIRouter(prefix="/persons", tags=["persons"])


@router.get("/", response_model=list[PersonRead])
def list_persons(db: Session = Depends(get_db)):
    return svc.list_persons(db)


@router.post("/", response_model=PersonRead, status_code=status.HTTP_201_CREATED)
def create_person(data: PersonCreate, db: Session = Depends(get_db)):
    return svc.create_person(db, data)


@router.get("/{person_id}", response_model=PersonRead)
def get_person(person_id: uuid.UUID, db: Session = Depends(get_db)):
    person = svc.get_person(db, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person


@router.patch("/{person_id}", response_model=PersonRead)
def update_person(person_id: uuid.UUID, data: PersonUpdate, db: Session = Depends(get_db)):
    person = svc.get_person(db, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return svc.update_person(db, person, data)


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_person(person_id: uuid.UUID, db: Session = Depends(get_db)):
    person = svc.get_person(db, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    svc.delete_person(db, person)
```

- [ ] **Step 9: Register router in `backend/app/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import persons

app = FastAPI(title="Atoms API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:80"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(persons.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
```

- [ ] **Step 10: Run tests — verify all pass**

```bash
make test
```

Expected: `8 passed`

- [ ] **Step 11: Commit**

```bash
git add backend/app/schemas/ backend/app/services/ backend/app/routers/ backend/app/main.py backend/tests/test_persons.py
git commit -m "feat: Person CRUD — TDD, soft-delete, organizations array"
```

---

## Task 8: Project CRUD (TDD)

**Files:**
- Create: `backend/app/schemas/project.py`
- Create: `backend/app/services/projects.py`
- Create: `backend/app/routers/projects.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_projects.py`

- [ ] **Step 1: Write failing tests — `backend/tests/test_projects.py`**

```python
import uuid


def test_create_project(client):
    resp = client.post("/projects/", json={"name": "CRM", "color": "#10B981", "icon": "🏢"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "CRM"
    assert data["color"] == "#10B981"
    assert data["icon"] == "🏢"


def test_create_project_minimal(client):
    resp = client.post("/projects/", json={"name": "Infrastruktur"})
    assert resp.status_code == 201
    assert resp.json()["color"] is None
    assert resp.json()["icon"] is None


def test_list_projects(client):
    client.post("/projects/", json={"name": "A"})
    client.post("/projects/", json={"name": "B"})
    resp = client.get("/projects/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_update_project(client):
    created = client.post("/projects/", json={"name": "Alt"}).json()
    resp = client.patch(f"/projects/{created['id']}", json={"name": "Neu", "color": "#FF0000"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Neu"
    assert resp.json()["color"] == "#FF0000"


def test_delete_project(client):
    created = client.post("/projects/", json={"name": "Temp"}).json()
    assert client.delete(f"/projects/{created['id']}").status_code == 204
    assert client.get(f"/projects/{created['id']}").status_code == 404


def test_get_nonexistent_project(client):
    assert client.get(f"/projects/{uuid.uuid4()}").status_code == 404
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
make test
```

Expected: 6 new failures.

- [ ] **Step 3: Create `backend/app/schemas/project.py`**

```python
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProjectCreate(BaseModel):
    name: str
    color: str | None = None
    icon: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    color: str | None = None
    icon: str | None = None


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    color: str | None
    icon: str | None
    created_at: datetime
    updated_at: datetime
```

- [ ] **Step 4: Create `backend/app/services/projects.py`**

```python
import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


def list_projects(db: Session) -> list[Project]:
    return db.query(Project).filter(Project.deleted_at.is_(None)).all()


def get_project(db: Session, project_id: uuid.UUID) -> Project | None:
    return (
        db.query(Project)
        .filter(Project.id == project_id, Project.deleted_at.is_(None))
        .first()
    )


def create_project(db: Session, data: ProjectCreate) -> Project:
    project = Project(**data.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def update_project(db: Session, project: Project, data: ProjectUpdate) -> Project:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project: Project) -> None:
    project.deleted_at = datetime.now(UTC)
    db.commit()
```

- [ ] **Step 5: Create `backend/app/routers/projects.py`**

```python
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import app.services.projects as svc
from app.deps import get_db
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=list[ProjectRead])
def list_projects(db: Session = Depends(get_db)):
    return svc.list_projects(db)


@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    return svc.create_project(db, data)


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: uuid.UUID, db: Session = Depends(get_db)):
    project = svc.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(project_id: uuid.UUID, data: ProjectUpdate, db: Session = Depends(get_db)):
    project = svc.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return svc.update_project(db, project, data)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: uuid.UUID, db: Session = Depends(get_db)):
    project = svc.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    svc.delete_project(db, project)
```

- [ ] **Step 6: Register router in `backend/app/main.py`**

```python
from app.routers import persons, projects

# add after existing include_router:
app.include_router(projects.router)
```

- [ ] **Step 7: Run tests — verify all pass**

```bash
make test
```

Expected: `14 passed`

- [ ] **Step 8: Commit**

```bash
git add backend/app/schemas/project.py backend/app/services/projects.py backend/app/routers/projects.py backend/app/main.py backend/tests/test_projects.py
git commit -m "feat: Project CRUD — TDD, soft-delete, color and icon fields"
```

---

## Task 9: Atom CRUD (TDD)

**Files:**
- Create: `backend/app/schemas/atom.py`
- Create: `backend/app/services/atoms.py`
- Create: `backend/app/routers/atoms.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_atoms.py`

- [ ] **Step 1: Write failing tests — `backend/tests/test_atoms.py`**

```python
import uuid
from datetime import UTC, datetime


def make_person(client, name="Anna"):
    return client.post("/persons/", json={"name": name}).json()


def make_project(client, name="CRM"):
    return client.post("/projects/", json={"name": name}).json()


def test_create_note(client):
    resp = client.post("/atoms/", json={"title": "Kundengespräch", "type": "note"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Kundengespräch"
    assert data["type"] == "note"
    assert data["captured"] is False
    assert data["content"] == ""
    assert data["responsible"] == []
    assert data["participants"] == []
    assert data["projects"] == []


def test_create_task_with_all_fields(client):
    person = make_person(client)
    project = make_project(client)
    resp = client.post("/atoms/", json={
        "title": "Report schreiben",
        "type": "task",
        "status": "open",
        "priority": "high",
        "complexity": "deep",
        "deadline_date": "2026-07-01T12:00:00Z",
        "responsible_ids": [person["id"]],
        "project_ids": [project["id"]],
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "open"
    assert data["priority"] == "high"
    assert data["complexity"] == "deep"
    assert len(data["responsible"]) == 1
    assert data["responsible"][0]["name"] == "Anna"
    assert len(data["projects"]) == 1


def test_list_atoms(client):
    client.post("/atoms/", json={"title": "A", "type": "note"})
    client.post("/atoms/", json={"title": "B", "type": "thought"})
    resp = client.get("/atoms/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_get_atom(client):
    created = client.post("/atoms/", json={"title": "Test", "type": "decision"}).json()
    resp = client.get(f"/atoms/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Test"


def test_update_atom_title(client):
    created = client.post("/atoms/", json={"title": "Alt", "type": "note"}).json()
    resp = client.patch(f"/atoms/{created['id']}", json={"title": "Neu"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "Neu"


def test_update_captured(client):
    created = client.post("/atoms/", json={"title": "Inbox item", "type": "thought"}).json()
    assert created["captured"] is False
    resp = client.patch(f"/atoms/{created['id']}", json={"captured": True})
    assert resp.status_code == 200
    assert resp.json()["captured"] is True


def test_update_relations(client):
    person = make_person(client, "Bob")
    project = make_project(client, "Infra")
    created = client.post("/atoms/", json={"title": "X", "type": "task"}).json()
    resp = client.patch(f"/atoms/{created['id']}", json={
        "participant_ids": [person["id"]],
        "project_ids": [project["id"]],
    })
    assert resp.status_code == 200
    assert len(resp.json()["participants"]) == 1
    assert len(resp.json()["projects"]) == 1


def test_delete_atom(client):
    created = client.post("/atoms/", json={"title": "Temp", "type": "note"}).json()
    assert client.delete(f"/atoms/{created['id']}").status_code == 204
    assert client.get(f"/atoms/{created['id']}").status_code == 404


def test_deleted_excluded_from_list(client):
    created = client.post("/atoms/", json={"title": "X", "type": "note"}).json()
    client.delete(f"/atoms/{created['id']}")
    resp = client.get("/atoms/")
    assert all(a["id"] != created["id"] for a in resp.json())


def test_filter_by_type(client):
    client.post("/atoms/", json={"title": "N", "type": "note"})
    client.post("/atoms/", json={"title": "T", "type": "task"})
    resp = client.get("/atoms/?type=note")
    assert resp.status_code == 200
    assert all(a["type"] == "note" for a in resp.json())


def test_filter_inbox(client):
    client.post("/atoms/", json={"title": "Uncaptured", "type": "note"})
    captured = client.post("/atoms/", json={"title": "Captured", "type": "note"}).json()
    client.patch(f"/atoms/{captured['id']}", json={"captured": True})
    resp = client.get("/atoms/?filter_badge=inbox")
    assert resp.status_code == 200
    assert all(a["captured"] is False for a in resp.json())


def test_filter_overdue(client):
    resp = client.post("/atoms/", json={
        "title": "Overdue task",
        "type": "task",
        "status": "open",
        "deadline_date": "2020-01-01T00:00:00Z",
    })
    assert resp.status_code == 201
    result = client.get("/atoms/?filter_badge=overdue").json()
    assert any(a["title"] == "Overdue task" for a in result)


def test_get_nonexistent_atom(client):
    assert client.get(f"/atoms/{uuid.uuid4()}").status_code == 404
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
make test
```

Expected: 13 new failures.

- [ ] **Step 3: Create `backend/app/schemas/atom.py`**

```python
import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.schemas.person import PersonRead
from app.schemas.project import ProjectRead

AtomType = Literal["note", "thought", "task", "decision"]
AtomStatus = Literal["open", "in_progress", "blocked", "done", "cancelled"]
AtomPriority = Literal["high", "medium", "low"]
AtomComplexity = Literal["deep", "shallow", "routine"]


class AtomCreate(BaseModel):
    title: str
    content: str = ""
    type: AtomType
    captured: bool = False
    status: AtomStatus | None = None
    priority: AtomPriority | None = None
    complexity: AtomComplexity | None = None
    deadline_date: datetime | None = None
    alarm_date: datetime | None = None
    source_url: str | None = None
    responsible_ids: list[uuid.UUID] = []
    participant_ids: list[uuid.UUID] = []
    project_ids: list[uuid.UUID] = []


class AtomUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    type: AtomType | None = None
    captured: bool | None = None
    status: AtomStatus | None = None
    priority: AtomPriority | None = None
    complexity: AtomComplexity | None = None
    deadline_date: datetime | None = None
    alarm_date: datetime | None = None
    source_url: str | None = None
    responsible_ids: list[uuid.UUID] | None = None
    participant_ids: list[uuid.UUID] | None = None
    project_ids: list[uuid.UUID] | None = None


class AtomRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    content: str
    type: str
    captured: bool
    status: str | None
    priority: str | None
    complexity: str | None
    deadline_date: datetime | None
    alarm_date: datetime | None
    source_url: str | None
    responsible: list[PersonRead]
    participants: list[PersonRead]
    projects: list[ProjectRead]
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
```

- [ ] **Step 4: Create `backend/app/services/atoms.py`**

```python
import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.atom import Atom
from app.models.person import Person
from app.models.project import Project
from app.schemas.atom import AtomCreate, AtomUpdate


def _resolve_relations(db: Session, atom: Atom, responsible_ids, participant_ids, project_ids):
    if responsible_ids is not None:
        atom.responsible = db.query(Person).filter(Person.id.in_(responsible_ids)).all()
    if participant_ids is not None:
        atom.participants = db.query(Person).filter(Person.id.in_(participant_ids)).all()
    if project_ids is not None:
        atom.projects = db.query(Project).filter(Project.id.in_(project_ids)).all()


def list_atoms(
    db: Session,
    type: str | None = None,
    filter_badge: str | None = None,
) -> list[Atom]:
    now = datetime.now(UTC)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    query = db.query(Atom).filter(Atom.deleted_at.is_(None))

    if type:
        query = query.filter(Atom.type == type)

    if filter_badge == "inbox":
        query = query.filter(Atom.captured.is_(False))
    elif filter_badge == "created_today":
        query = query.filter(Atom.created_at >= today_start)
    elif filter_badge == "updated_today":
        query = query.filter(Atom.updated_at >= today_start)
    elif filter_badge == "overdue":
        query = query.filter(
            Atom.type == "task",
            Atom.deadline_date < now,
            Atom.status.notin_(["done", "cancelled"]),
        )

    return query.order_by(Atom.created_at.desc()).all()


def get_atom(db: Session, atom_id: uuid.UUID) -> Atom | None:
    return (
        db.query(Atom)
        .filter(Atom.id == atom_id, Atom.deleted_at.is_(None))
        .first()
    )


def create_atom(db: Session, data: AtomCreate) -> Atom:
    scalar_data = data.model_dump(exclude={"responsible_ids", "participant_ids", "project_ids"})
    atom = Atom(**scalar_data)
    _resolve_relations(db, atom, data.responsible_ids, data.participant_ids, data.project_ids)
    db.add(atom)
    db.commit()
    db.refresh(atom)
    return atom


def update_atom(db: Session, atom: Atom, data: AtomUpdate) -> Atom:
    update_data = data.model_dump(exclude_unset=True)
    responsible_ids = update_data.pop("responsible_ids", None)
    participant_ids = update_data.pop("participant_ids", None)
    project_ids = update_data.pop("project_ids", None)

    for field, value in update_data.items():
        setattr(atom, field, value)

    _resolve_relations(db, atom, responsible_ids, participant_ids, project_ids)
    db.commit()
    db.refresh(atom)
    return atom


def delete_atom(db: Session, atom: Atom) -> None:
    atom.deleted_at = datetime.now(UTC)
    db.commit()
```

- [ ] **Step 5: Create `backend/app/routers/atoms.py`**

```python
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import app.services.atoms as svc
from app.deps import get_db
from app.schemas.atom import AtomCreate, AtomRead, AtomUpdate

router = APIRouter(prefix="/atoms", tags=["atoms"])


@router.get("/", response_model=list[AtomRead])
def list_atoms(
    type: str | None = None,
    filter_badge: str | None = None,
    db: Session = Depends(get_db),
):
    return svc.list_atoms(db, type=type, filter_badge=filter_badge)


@router.post("/", response_model=AtomRead, status_code=status.HTTP_201_CREATED)
def create_atom(data: AtomCreate, db: Session = Depends(get_db)):
    return svc.create_atom(db, data)


@router.get("/{atom_id}", response_model=AtomRead)
def get_atom(atom_id: uuid.UUID, db: Session = Depends(get_db)):
    atom = svc.get_atom(db, atom_id)
    if not atom:
        raise HTTPException(status_code=404, detail="Atom not found")
    return atom


@router.patch("/{atom_id}", response_model=AtomRead)
def update_atom(atom_id: uuid.UUID, data: AtomUpdate, db: Session = Depends(get_db)):
    atom = svc.get_atom(db, atom_id)
    if not atom:
        raise HTTPException(status_code=404, detail="Atom not found")
    return svc.update_atom(db, atom, data)


@router.delete("/{atom_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_atom(atom_id: uuid.UUID, db: Session = Depends(get_db)):
    atom = svc.get_atom(db, atom_id)
    if not atom:
        raise HTTPException(status_code=404, detail="Atom not found")
    svc.delete_atom(db, atom)
```

- [ ] **Step 6: Register router in `backend/app/main.py`**

```python
from app.routers import atoms, persons, projects

app.include_router(atoms.router)
```

- [ ] **Step 7: Run tests — verify all pass**

```bash
make test
```

Expected: `27 passed`

- [ ] **Step 8: Commit**

```bash
git add backend/app/schemas/atom.py backend/app/services/atoms.py backend/app/routers/atoms.py backend/app/main.py backend/tests/test_atoms.py
git commit -m "feat: Atom CRUD — TDD, all types, M2M relations, filter_badge query param"
```

---

## Task 10: Frontend API Client + Types

**Files:**
- Create: `frontend/src/lib/api/types.ts`
- Create: `frontend/src/lib/api/client.ts`
- Create: `frontend/src/lib/api/atoms.ts`
- Create: `frontend/src/lib/api/persons.ts`
- Create: `frontend/src/lib/api/projects.ts`

- [ ] **Step 1: Create `frontend/src/lib/api/types.ts`**

```typescript
export type AtomType = 'note' | 'thought' | 'task' | 'decision'
export type AtomStatus = 'open' | 'in_progress' | 'blocked' | 'done' | 'cancelled'
export type AtomPriority = 'high' | 'medium' | 'low'
export type AtomComplexity = 'deep' | 'shallow' | 'routine'
export type FilterBadge = 'inbox' | 'created_today' | 'updated_today' | 'overdue'

export interface Person {
  id: string
  name: string
  photo_url: string | null
  organizations: string[]
  created_at: string
  updated_at: string
}

export interface Project {
  id: string
  name: string
  color: string | null
  icon: string | null
  created_at: string
  updated_at: string
}

export interface Atom {
  id: string
  title: string
  content: string
  type: AtomType
  captured: boolean
  status: AtomStatus | null
  priority: AtomPriority | null
  complexity: AtomComplexity | null
  deadline_date: string | null
  alarm_date: string | null
  source_url: string | null
  responsible: Person[]
  participants: Person[]
  projects: Project[]
  created_at: string
  updated_at: string
  deleted_at: string | null
}

export interface AtomCreate {
  title: string
  type: AtomType
  content?: string
  captured?: boolean
  status?: AtomStatus | null
  priority?: AtomPriority | null
  complexity?: AtomComplexity | null
  deadline_date?: string | null
  alarm_date?: string | null
  source_url?: string | null
  responsible_ids?: string[]
  participant_ids?: string[]
  project_ids?: string[]
}

export interface AtomUpdate {
  title?: string
  content?: string
  type?: AtomType
  captured?: boolean
  status?: AtomStatus | null
  priority?: AtomPriority | null
  complexity?: AtomComplexity | null
  deadline_date?: string | null
  alarm_date?: string | null
  source_url?: string | null
  responsible_ids?: string[]
  participant_ids?: string[]
  project_ids?: string[]
}

export interface PersonCreate {
  name: string
  photo_url?: string | null
  organizations?: string[]
}

export interface ProjectCreate {
  name: string
  color?: string | null
  icon?: string | null
}
```

- [ ] **Step 2: Create `frontend/src/lib/api/client.ts`**

```typescript
const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error((err as { detail: string }).detail ?? `HTTP ${res.status}`)
  }
  if (res.status === 204) return undefined as T
  return res.json() as Promise<T>
}
```

- [ ] **Step 3: Create `frontend/src/lib/api/atoms.ts`**

```typescript
import { api } from './client'
import type { Atom, AtomCreate, AtomUpdate, FilterBadge } from './types'

export function getAtoms(params?: { type?: string; filter_badge?: FilterBadge }): Promise<Atom[]> {
  const q = new URLSearchParams()
  if (params?.type) q.set('type', params.type)
  if (params?.filter_badge) q.set('filter_badge', params.filter_badge)
  return api<Atom[]>(`/atoms/?${q}`)
}

export function getAtom(id: string): Promise<Atom> {
  return api<Atom>(`/atoms/${id}`)
}

export function createAtom(data: AtomCreate): Promise<Atom> {
  return api<Atom>('/atoms/', { method: 'POST', body: JSON.stringify(data) })
}

export function updateAtom(id: string, data: AtomUpdate): Promise<Atom> {
  return api<Atom>(`/atoms/${id}`, { method: 'PATCH', body: JSON.stringify(data) })
}

export function deleteAtom(id: string): Promise<void> {
  return api<void>(`/atoms/${id}`, { method: 'DELETE' })
}
```

- [ ] **Step 4: Create `frontend/src/lib/api/persons.ts`**

```typescript
import { api } from './client'
import type { Person, PersonCreate } from './types'

export function getPersons(): Promise<Person[]> {
  return api<Person[]>('/persons/')
}

export function createPerson(data: PersonCreate): Promise<Person> {
  return api<Person>('/persons/', { method: 'POST', body: JSON.stringify(data) })
}
```

- [ ] **Step 5: Create `frontend/src/lib/api/projects.ts`**

```typescript
import { api } from './client'
import type { Project, ProjectCreate } from './types'

export function getProjects(): Promise<Project[]> {
  return api<Project[]>('/projects/')
}

export function createProject(data: ProjectCreate): Promise<Project> {
  return api<Project>('/projects/', { method: 'POST', body: JSON.stringify(data) })
}
```

- [ ] **Step 6: Commit**

```bash
git add frontend/src/lib/api/
git commit -m "feat: frontend API client — typed fetch wrapper, atoms/persons/projects"
```

---

## Task 11: Reusable Components

**Files:**
- Create: `frontend/src/lib/components/TypeIcon.svelte`
- Create: `frontend/src/lib/components/PersonAvatar.svelte`
- Create: `frontend/src/lib/components/ProjectBadge.svelte`

- [ ] **Step 1: Create `frontend/src/lib/components/TypeIcon.svelte`**

```svelte
<script lang="ts">
  import type { AtomType } from '$lib/api/types'

  let { type }: { type: AtomType } = $props()

  const cfg: Record<AtomType, { symbol: string; color: string; label: string }> = {
    note:     { symbol: '□',  color: '#6B7280', label: 'Notiz' },
    thought:  { symbol: '◎',  color: '#8B5CF6', label: 'Gedanke' },
    task:     { symbol: '☐',  color: '#10B981', label: 'Aufgabe' },
    decision: { symbol: '◆',  color: '#F59E0B', label: 'Entscheidung' },
  }
</script>

<span class="icon" style="color: {cfg[type].color}" title={cfg[type].label}>
  {cfg[type].symbol}
</span>

<style>
  .icon {
    font-size: 0.85rem;
    width: 1.2rem;
    display: inline-block;
    text-align: center;
    flex-shrink: 0;
  }
</style>
```

- [ ] **Step 2: Create `frontend/src/lib/components/PersonAvatar.svelte`**

```svelte
<script lang="ts">
  import type { Person } from '$lib/api/types'

  let { person }: { person: Person } = $props()

  const COLORS = ['#10B981','#8B5CF6','#F59E0B','#3B82F6','#EF4444','#06B6D4','#EC4899']

  function initials(name: string): string {
    return name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase()
  }

  function bg(name: string): string {
    let h = 0
    for (const c of name) h = (h * 31 + c.charCodeAt(0)) >>> 0
    return COLORS[h % COLORS.length]
  }
</script>

<span class="avatar" style="background: {bg(person.name)}" title={person.name}>
  {#if person.photo_url}
    <img src={person.photo_url} alt={person.name} />
  {:else}
    {initials(person.name)}
  {/if}
</span>

<style>
  .avatar {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 1.75rem;
    height: 1.75rem;
    border-radius: 50%;
    color: white;
    font-size: 0.65rem;
    font-weight: 600;
    overflow: hidden;
    flex-shrink: 0;
  }
  .avatar img { width: 100%; height: 100%; object-fit: cover; }
</style>
```

- [ ] **Step 3: Create `frontend/src/lib/components/ProjectBadge.svelte`**

```svelte
<script lang="ts">
  import type { Project } from '$lib/api/types'

  let { project }: { project: Project } = $props()

  const borderColor = project.color ?? '#10B981'
  const textColor = project.color ?? '#10B981'
</script>

<span class="badge" style="border-color: {borderColor}; color: {textColor}">
  {#if project.icon}{project.icon}&nbsp;{/if}{project.name}
</span>

<style>
  .badge {
    display: inline-block;
    padding: 0.1rem 0.4rem;
    border: 1px solid;
    border-radius: 4px;
    font-size: 0.72rem;
    white-space: nowrap;
    line-height: 1.4;
  }
</style>
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/lib/components/TypeIcon.svelte frontend/src/lib/components/PersonAvatar.svelte frontend/src/lib/components/ProjectBadge.svelte
git commit -m "feat: reusable components — TypeIcon, PersonAvatar, ProjectBadge"
```

---

## Task 12: List View

**Files:**
- Create: `frontend/src/lib/components/FilterBadges.svelte`
- Create: `frontend/src/lib/components/AtomRow.svelte`
- Modify: `frontend/src/routes/+page.svelte`

- [ ] **Step 1: Create `frontend/src/lib/components/FilterBadges.svelte`**

```svelte
<script lang="ts">
  import type { FilterBadge } from '$lib/api/types'

  let { active = $bindable(null) }: { active?: FilterBadge | null } = $props()

  const badges: { id: FilterBadge; label: string }[] = [
    { id: 'inbox',        label: 'Inbox' },
    { id: 'created_today', label: 'Heute erstellt' },
    { id: 'updated_today', label: 'Heute geändert' },
    { id: 'overdue',      label: 'Überfällig' },
  ]

  function toggle(id: FilterBadge) {
    active = active === id ? null : id
  }
</script>

<div class="badges">
  {#each badges as badge}
    <button
      class="badge"
      class:active={active === badge.id}
      onclick={() => toggle(badge.id)}
    >
      {badge.label}
    </button>
  {/each}
</div>

<style>
  .badges {
    display: flex;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    border-bottom: 1px solid var(--border);
  }
  .badge {
    padding: 0.3rem 0.75rem;
    border: 1px solid var(--border);
    border-radius: 999px;
    background: transparent;
    color: var(--text-muted);
    font-size: 0.8rem;
    transition: all 0.1s;
  }
  .badge:hover { border-color: var(--accent); color: var(--accent); }
  .badge.active { background: var(--accent); border-color: var(--accent); color: white; }
</style>
```

- [ ] **Step 2: Create `frontend/src/lib/components/AtomRow.svelte`**

```svelte
<script lang="ts">
  import type { Atom } from '$lib/api/types'
  import TypeIcon from './TypeIcon.svelte'
  import PersonAvatar from './PersonAvatar.svelte'
  import ProjectBadge from './ProjectBadge.svelte'

  let {
    atom,
    selected = false,
    expanded = false,
    onselect,
    oncapturedtoggle,
  }: {
    atom: Atom
    selected?: boolean
    expanded?: boolean
    onselect: (atom: Atom) => void
    oncapturedtoggle: (atom: Atom) => void
  } = $props()

  let rowExpanded = $state(false)
  let isExpanded = $derived(expanded || rowExpanded)

  const STATUS_LABELS: Record<string, string> = {
    open: 'Offen', in_progress: 'Läuft', blocked: 'Blockiert',
    done: 'Erledigt', cancelled: 'Abgebrochen',
  }
  const PRIORITY_LABELS: Record<string, string> = {
    high: 'Hoch', medium: 'Mittel', low: 'Niedrig',
  }
</script>

<div
  class="row"
  class:selected
  class:done={atom.status === 'done'}
  role="button"
  tabindex="0"
  onclick={() => onselect(atom)}
  onkeydown={(e) => e.key === 'Enter' && onselect(atom)}
>
  <div class="row-main">
    <button
      class="expand-btn"
      onclick|stopPropagation={() => (rowExpanded = !rowExpanded)}
      aria-label="Aufklappen"
    >
      {isExpanded ? '∨' : '›'}
    </button>

    <TypeIcon type={atom.type} />

    <span class="title" class:strikethrough={atom.status === 'done'}>
      {atom.title}
    </span>

    <div class="meta">
      {#if atom.type === 'task' && atom.status}
        <span class="status-badge status-{atom.status}">
          {STATUS_LABELS[atom.status] ?? atom.status}
        </span>
      {/if}

      {#if atom.type === 'task' && atom.priority}
        <span class="prio prio-{atom.priority}">
          {PRIORITY_LABELS[atom.priority] ?? atom.priority}
        </span>
      {/if}

      {#if atom.type === 'task' && atom.deadline_date}
        <span class="deadline">
          {new Date(atom.deadline_date).toLocaleDateString('de-DE', { day:'numeric', month:'numeric' })}
        </span>
      {/if}

      <div class="avatars">
        {#each atom.responsible as person}
          <PersonAvatar {person} />
        {/each}
      </div>

      <div class="projects">
        {#each atom.projects as project}
          <ProjectBadge {project} />
        {/each}
      </div>

      <button
        class="captured-btn"
        class:is-captured={atom.captured}
        onclick|stopPropagation={() => oncapturedtoggle(atom)}
        title={atom.captured ? 'Erfasst' : 'Nicht erfasst'}
        aria-label="Erfasst togglen"
      >
        {atom.captured ? '✓' : '○'}
      </button>
    </div>
  </div>

  {#if isExpanded && atom.content}
    <div class="preview">{atom.content}</div>
  {/if}
</div>

<style>
  .row {
    border-bottom: 1px solid var(--border);
    cursor: pointer;
    transition: background 0.1s;
  }
  .row:hover { background: var(--bg-hover); }
  .row.selected { border-left: 3px solid var(--accent); }
  .row-main {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.6rem 1rem;
    min-height: 2.5rem;
  }
  .expand-btn {
    background: none;
    border: none;
    color: var(--text-muted);
    padding: 0 0.25rem;
    font-size: 0.75rem;
    line-height: 1;
    flex-shrink: 0;
  }
  .title {
    flex: 1;
    font-size: 0.875rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .strikethrough { text-decoration: line-through; color: var(--text-muted); }
  .meta {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-shrink: 0;
  }
  .status-badge {
    font-size: 0.72rem;
    padding: 0.1rem 0.4rem;
    border-radius: 4px;
    background: var(--border);
  }
  .status-done { color: var(--accent); background: var(--accent-light); }
  .prio { font-size: 0.72rem; color: var(--text-muted); }
  .prio-high { color: #EF4444; }
  .deadline { font-size: 0.72rem; color: var(--text-muted); }
  .avatars, .projects { display: flex; gap: 0.2rem; align-items: center; }
  .captured-btn {
    background: none;
    border: none;
    font-size: 0.85rem;
    color: var(--text-muted);
    padding: 0.1rem 0.3rem;
  }
  .captured-btn.is-captured { color: var(--accent); }
  .preview {
    padding: 0.25rem 1rem 0.6rem 3rem;
    font-size: 0.8rem;
    color: var(--text-muted);
    white-space: pre-wrap;
    word-break: break-word;
  }
</style>
```

- [ ] **Step 3: Replace `frontend/src/routes/+page.svelte`**

```svelte
<script lang="ts">
  import { onMount } from 'svelte'
  import type { Atom, FilterBadge } from '$lib/api/types'
  import { getAtoms, updateAtom, deleteAtom } from '$lib/api/atoms'
  import AtomRow from '$lib/components/AtomRow.svelte'
  import FilterBadges from '$lib/components/FilterBadges.svelte'

  let atoms = $state<Atom[]>([])
  let selectedAtom = $state<Atom | null>(null)
  let activeFilter = $state<FilterBadge | null>(null)
  let allExpanded = $state(false)
  let loading = $state(true)
  let error = $state<string | null>(null)

  async function load() {
    loading = true
    error = null
    try {
      atoms = await getAtoms(activeFilter ? { filter_badge: activeFilter } : {})
    } catch (e) {
      error = (e as Error).message
    } finally {
      loading = false
    }
  }

  onMount(load)

  $effect(() => {
    void activeFilter
    load()
  })

  async function handleCapturedToggle(atom: Atom) {
    const updated = await updateAtom(atom.id, { captured: !atom.captured })
    atoms = atoms.map(a => a.id === atom.id ? updated : a)
    if (selectedAtom?.id === atom.id) selectedAtom = updated
  }

  function handleSelect(atom: Atom) {
    selectedAtom = selectedAtom?.id === atom.id ? null : atom
  }
</script>

<div class="app">
  <header>
    <div class="brand">
      <span class="logo">⬡</span>
      <span class="app-name">Atoms</span>
    </div>
    <div class="header-actions">
      <button class="btn-ghost" class:active={!allExpanded} onclick={() => (allExpanded = false)}>
        Kompakt
      </button>
      <button class="btn-ghost" class:active={allExpanded} onclick={() => (allExpanded = true)}>
        Detail
      </button>
      <button class="btn-primary">+ Neu</button>
    </div>
  </header>

  <FilterBadges bind:active={activeFilter} />

  <div class="content" class:panel-open={!!selectedAtom}>
    <div class="list-area">
      {#if loading}
        <p class="empty">Lade…</p>
      {:else if error}
        <p class="empty error">{error}</p>
      {:else if atoms.length === 0}
        <p class="empty">Keine Einträge.</p>
      {:else}
        {#each atoms as atom (atom.id)}
          <AtomRow
            {atom}
            selected={selectedAtom?.id === atom.id}
            expanded={allExpanded}
            onselect={handleSelect}
            oncapturedtoggle={handleCapturedToggle}
          />
        {/each}
      {/if}
    </div>

    {#if selectedAtom}
      <div class="panel-placeholder">
        <p style="padding:1rem; color: var(--text-muted)">Panel kommt in Task 13</p>
        <button onclick={() => (selectedAtom = null)}>✕</button>
      </div>
    {/if}
  </div>
</div>

<style>
  .app { display: flex; flex-direction: column; height: 100vh; overflow: hidden; }

  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 1.5rem;
    height: 3.5rem;
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
  }
  .brand { display: flex; align-items: center; gap: 0.5rem; }
  .logo { font-size: 1.3rem; color: var(--accent); }
  .app-name { font-weight: 600; font-size: 1rem; }
  .header-actions { display: flex; gap: 0.5rem; align-items: center; }

  .btn-ghost {
    background: none;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.35rem 0.75rem;
    font-size: 0.8rem;
    color: var(--text-muted);
  }
  .btn-ghost.active { border-color: var(--accent); color: var(--accent); }
  .btn-primary {
    background: var(--accent);
    border: none;
    border-radius: 6px;
    padding: 0.4rem 0.9rem;
    color: white;
    font-size: 0.85rem;
    font-weight: 500;
  }

  .content { display: flex; flex: 1; overflow: hidden; }
  .list-area { flex: 1; overflow-y: auto; }
  .panel-placeholder {
    width: 360px;
    border-left: 1px solid var(--border);
    flex-shrink: 0;
  }
  .content.panel-open .list-area { flex: 1; }

  .empty { padding: 2rem 1.5rem; color: var(--text-muted); font-size: 0.875rem; }
  .error { color: #EF4444; }
</style>
```

- [ ] **Step 4: Open browser at `http://localhost:5173` and verify**

Expected: header with "Atoms" logo, filter badges row, list of atoms (empty if DB is fresh). Clicking a badge loads filtered results. Clicking captured toggle updates immediately.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/lib/components/FilterBadges.svelte frontend/src/lib/components/AtomRow.svelte frontend/src/routes/+page.svelte
git commit -m "feat: list view — AtomRow, FilterBadges, compact/detail toggle, captured toggle"
```

---

## Task 13: Panel

**Files:**
- Create: `frontend/src/lib/components/AtomPanel.svelte`
- Modify: `frontend/src/routes/+page.svelte`

- [ ] **Step 1: Create `frontend/src/lib/components/AtomPanel.svelte`**

```svelte
<script lang="ts">
  import type { Atom, AtomUpdate, AtomType, AtomStatus, AtomPriority, AtomComplexity, Person, Project } from '$lib/api/types'
  import PersonAvatar from './PersonAvatar.svelte'
  import ProjectBadge from './ProjectBadge.svelte'
  import TypeIcon from './TypeIcon.svelte'

  let {
    atom,
    allPersons,
    allProjects,
    onsave,
    ondelete,
    onclose,
  }: {
    atom: Atom
    allPersons: Person[]
    allProjects: Project[]
    onsave: (id: string, data: AtomUpdate) => Promise<void>
    ondelete: (id: string) => Promise<void>
    onclose: () => void
  } = $props()

  let title = $state(atom.title)
  let content = $state(atom.content)
  let type = $state<AtomType>(atom.type)
  let captured = $state(atom.captured)
  let status = $state<AtomStatus | null>(atom.status)
  let priority = $state<AtomPriority | null>(atom.priority)
  let complexity = $state<AtomComplexity | null>(atom.complexity)
  let deadline_date = $state(atom.deadline_date ? atom.deadline_date.slice(0, 16) : '')
  let alarm_date = $state(atom.alarm_date ? atom.alarm_date.slice(0, 16) : '')
  let source_url = $state(atom.source_url ?? '')
  let responsible_ids = $state(atom.responsible.map(p => p.id))
  let participant_ids = $state(atom.participants.map(p => p.id))
  let project_ids = $state(atom.projects.map(p => p.id))

  let saving = $state(false)
  let confirmDelete = $state(false)

  $effect(() => {
    title = atom.title
    content = atom.content
    type = atom.type
    captured = atom.captured
    status = atom.status
    priority = atom.priority
    complexity = atom.complexity
    deadline_date = atom.deadline_date ? atom.deadline_date.slice(0, 16) : ''
    alarm_date = atom.alarm_date ? atom.alarm_date.slice(0, 16) : ''
    source_url = atom.source_url ?? ''
    responsible_ids = atom.responsible.map(p => p.id)
    participant_ids = atom.participants.map(p => p.id)
    project_ids = atom.projects.map(p => p.id)
  })

  async function save() {
    saving = true
    await onsave(atom.id, {
      title, content, type, captured, status, priority, complexity,
      deadline_date: deadline_date ? new Date(deadline_date).toISOString() : null,
      alarm_date: alarm_date ? new Date(alarm_date).toISOString() : null,
      source_url: source_url || null,
      responsible_ids,
      participant_ids,
      project_ids,
    })
    saving = false
  }

  async function handleDelete() {
    if (!confirmDelete) { confirmDelete = true; return }
    await ondelete(atom.id)
  }

  function toggleId(ids: string[], id: string): string[] {
    return ids.includes(id) ? ids.filter(x => x !== id) : [...ids, id]
  }

  const TYPE_LABELS: Record<AtomType, string> = {
    note: 'Notiz', thought: 'Gedanke', task: 'Aufgabe', decision: 'Entscheidung'
  }
  const STATUS_LABELS: Record<AtomStatus, string> = {
    open: 'Offen', in_progress: 'Läuft', blocked: 'Blockiert', done: 'Erledigt', cancelled: 'Abgebrochen'
  }
  const PRIORITY_LABELS: Record<AtomPriority, string> = {
    high: 'Hoch', medium: 'Mittel', low: 'Niedrig'
  }
  const COMPLEXITY_LABELS: Record<AtomComplexity, string> = {
    deep: 'Tiefe Arbeit', shallow: 'Oberflächlich', routine: 'Routine'
  }
</script>

<aside class="panel">
  <div class="panel-header">
    <TypeIcon {type} />
    <input class="title-input" bind:value={title} placeholder="Titel" />
    <button class="close-btn" onclick={onclose} aria-label="Schließen">✕</button>
  </div>

  <div class="panel-body">
    <textarea class="content-input" bind:value={content} placeholder="Inhalt (Markdown)…" rows="5"></textarea>

    <section>
      <h3>Kompakt-Felder</h3>

      <div class="field">
        <label>Typ</label>
        <select bind:value={type}>
          {#each Object.entries(TYPE_LABELS) as [val, label]}
            <option value={val}>{label}</option>
          {/each}
        </select>
      </div>

      <div class="field">
        <label>Verantwortlich</label>
        <div class="person-list">
          {#each allPersons as person}
            <button
              class="person-chip"
              class:selected={responsible_ids.includes(person.id)}
              onclick={() => responsible_ids = toggleId(responsible_ids, person.id)}
            >
              <PersonAvatar {person} />
              <span>{person.name}</span>
            </button>
          {/each}
          {#if allPersons.length === 0}
            <span class="muted">Keine Personen vorhanden</span>
          {/if}
        </div>
      </div>

      <div class="field">
        <label>Beteiligt</label>
        <div class="person-list">
          {#each allPersons as person}
            <button
              class="person-chip"
              class:selected={participant_ids.includes(person.id)}
              onclick={() => participant_ids = toggleId(participant_ids, person.id)}
            >
              <PersonAvatar {person} />
              <span>{person.name}</span>
            </button>
          {/each}
        </div>
      </div>

      <div class="field">
        <label>Projekte</label>
        <div class="project-list">
          {#each allProjects as project}
            <button
              class="project-chip"
              class:selected={project_ids.includes(project.id)}
              onclick={() => project_ids = toggleId(project_ids, project.id)}
            >
              <ProjectBadge {project} />
            </button>
          {/each}
          {#if allProjects.length === 0}
            <span class="muted">Keine Projekte vorhanden</span>
          {/if}
        </div>
      </div>

      <div class="field captured-field">
        <label>Erfasst</label>
        <button
          class="captured-toggle"
          class:active={captured}
          onclick={() => captured = !captured}
        >
          {captured ? '✓ Erfasst' : '○ Nicht erfasst'}
        </button>
      </div>
    </section>

    {#if type === 'task'}
      <section>
        <h3>Aufgaben-Felder</h3>

        <div class="field">
          <label>Status</label>
          <select bind:value={status}>
            <option value={null}>—</option>
            {#each Object.entries(STATUS_LABELS) as [val, label]}
              <option value={val}>{label}</option>
            {/each}
          </select>
        </div>

        <div class="field">
          <label>Priorität</label>
          <select bind:value={priority}>
            <option value={null}>—</option>
            {#each Object.entries(PRIORITY_LABELS) as [val, label]}
              <option value={val}>{label}</option>
            {/each}
          </select>
        </div>

        <div class="field">
          <label>Komplexität</label>
          <select bind:value={complexity}>
            <option value={null}>—</option>
            {#each Object.entries(COMPLEXITY_LABELS) as [val, label]}
              <option value={val}>{label}</option>
            {/each}
          </select>
        </div>

        <div class="field">
          <label>Fälligkeit</label>
          <input type="datetime-local" bind:value={deadline_date} />
        </div>

        <div class="field">
          <label>Wecker</label>
          <input type="datetime-local" bind:value={alarm_date} />
        </div>
      </section>
    {/if}

    <section>
      <h3>Nur Panel</h3>

      <div class="field">
        <label>Quelle</label>
        <input type="url" bind:value={source_url} placeholder="https://…" />
      </div>

      <div class="field readonly">
        <label>Erstellt</label>
        <span>{new Date(atom.created_at).toLocaleString('de-DE')}</span>
      </div>

      <div class="field readonly">
        <label>Geändert</label>
        <span>{new Date(atom.updated_at).toLocaleString('de-DE')}</span>
      </div>
    </section>
  </div>

  <div class="panel-footer">
    <button
      class="btn-danger"
      onclick={handleDelete}
      class:confirm={confirmDelete}
    >
      {confirmDelete ? 'Wirklich löschen?' : 'Löschen'}
    </button>
    <button class="btn-save" onclick={save} disabled={saving}>
      {saving ? 'Speichere…' : 'Speichern'}
    </button>
  </div>
</aside>

<style>
  .panel {
    width: 360px;
    border-left: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    flex-shrink: 0;
    background: var(--bg);
    overflow: hidden;
  }
  .panel-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
  }
  .title-input {
    flex: 1;
    border: none;
    outline: none;
    font-size: 0.95rem;
    font-weight: 500;
    color: var(--text);
    background: transparent;
  }
  .close-btn {
    background: none;
    border: none;
    color: var(--text-muted);
    font-size: 1rem;
    padding: 0.2rem;
  }
  .panel-body {
    flex: 1;
    overflow-y: auto;
    padding: 0.75rem 1rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  .content-input {
    width: 100%;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.5rem;
    font-size: 0.8rem;
    resize: vertical;
    outline: none;
    background: var(--bg-hover);
  }
  section h3 {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin: 0 0 0.5rem;
  }
  .field {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    margin-bottom: 0.6rem;
  }
  .field label {
    width: 6rem;
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding-top: 0.2rem;
    flex-shrink: 0;
  }
  .field select, .field input[type="url"], .field input[type="datetime-local"] {
    flex: 1;
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 0.25rem 0.5rem;
    font-size: 0.8rem;
    background: var(--bg);
    color: var(--text);
  }
  .field.readonly span { font-size: 0.8rem; color: var(--text-muted); padding-top: 0.2rem; }
  .person-list, .project-list {
    flex: 1;
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
  }
  .person-chip, .project-chip {
    display: flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.2rem 0.5rem;
    border: 1px solid var(--border);
    border-radius: 999px;
    background: transparent;
    font-size: 0.75rem;
    cursor: pointer;
    opacity: 0.5;
  }
  .person-chip.selected, .project-chip.selected {
    opacity: 1;
    border-color: var(--accent);
  }
  .captured-toggle {
    background: none;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.25rem 0.6rem;
    font-size: 0.8rem;
    cursor: pointer;
    color: var(--text-muted);
  }
  .captured-toggle.active { border-color: var(--accent); color: var(--accent); }
  .muted { font-size: 0.75rem; color: var(--text-muted); }
  .panel-footer {
    display: flex;
    justify-content: space-between;
    padding: 0.75rem 1rem;
    border-top: 1px solid var(--border);
    flex-shrink: 0;
  }
  .btn-save {
    background: var(--accent);
    border: none;
    border-radius: 6px;
    padding: 0.4rem 1rem;
    color: white;
    font-size: 0.85rem;
    font-weight: 500;
  }
  .btn-save:disabled { opacity: 0.6; }
  .btn-danger {
    background: none;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.4rem 0.75rem;
    font-size: 0.8rem;
    color: var(--text-muted);
  }
  .btn-danger.confirm { border-color: #EF4444; color: #EF4444; }
</style>
```

- [ ] **Step 2: Update `frontend/src/routes/+page.svelte`** — replace panel placeholder, add person/project loading, wire save/delete

Replace the `<script>` block and panel section:

```svelte
<script lang="ts">
  import { onMount } from 'svelte'
  import type { Atom, AtomUpdate, FilterBadge, Person, Project } from '$lib/api/types'
  import { getAtoms, updateAtom, deleteAtom } from '$lib/api/atoms'
  import { getPersons } from '$lib/api/persons'
  import { getProjects } from '$lib/api/projects'
  import AtomRow from '$lib/components/AtomRow.svelte'
  import FilterBadges from '$lib/components/FilterBadges.svelte'
  import AtomPanel from '$lib/components/AtomPanel.svelte'

  let atoms = $state<Atom[]>([])
  let allPersons = $state<Person[]>([])
  let allProjects = $state<Project[]>([])
  let selectedAtom = $state<Atom | null>(null)
  let activeFilter = $state<FilterBadge | null>(null)
  let allExpanded = $state(false)
  let loading = $state(true)
  let error = $state<string | null>(null)

  async function load() {
    loading = true
    error = null
    try {
      atoms = await getAtoms(activeFilter ? { filter_badge: activeFilter } : {})
    } catch (e) {
      error = (e as Error).message
    } finally {
      loading = false
    }
  }

  onMount(async () => {
    await Promise.all([load(), getPersons().then(p => allPersons = p), getProjects().then(p => allProjects = p)])
  })

  $effect(() => {
    void activeFilter
    load()
  })

  async function handleCapturedToggle(atom: Atom) {
    const updated = await updateAtom(atom.id, { captured: !atom.captured })
    atoms = atoms.map(a => a.id === atom.id ? updated : a)
    if (selectedAtom?.id === atom.id) selectedAtom = updated
  }

  function handleSelect(atom: Atom) {
    selectedAtom = selectedAtom?.id === atom.id ? null : atom
  }

  async function handleSave(id: string, data: AtomUpdate) {
    const updated = await updateAtom(id, data)
    atoms = atoms.map(a => a.id === id ? updated : a)
    selectedAtom = updated
  }

  async function handleDelete(id: string) {
    await deleteAtom(id)
    atoms = atoms.filter(a => a.id !== id)
    selectedAtom = null
  }
</script>
```

And replace the panel placeholder in the template:

```svelte
    {#if selectedAtom}
      <AtomPanel
        atom={selectedAtom}
        {allPersons}
        {allProjects}
        onsave={handleSave}
        ondelete={handleDelete}
        onclose={() => (selectedAtom = null)}
      />
    {/if}
```

- [ ] **Step 3: Verify in browser**

Open `http://localhost:5173`. Click any atom row — panel slides in on the right. Edit a field, click Speichern. Row updates in the list. Click Löschen twice — atom disappears.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/lib/components/AtomPanel.svelte frontend/src/routes/+page.svelte
git commit -m "feat: AtomPanel — edit all fields, save, soft-delete with confirm"
```

---

## Task 14: New Atom Flow

**Files:**
- Modify: `frontend/src/routes/+page.svelte`

- [ ] **Step 1: Add new atom state and handler to `+page.svelte` `<script>`**

Add these imports and state variables after the existing ones:

```svelte
  import { createAtom } from '$lib/api/atoms'
  import type { AtomCreate } from '$lib/api/types'

  let isNewAtom = $state(false)
  let newAtomDraft = $state<Atom | null>(null)
```

Add `handleNew` and `handleNewSave` functions:

```svelte
  async function handleNew() {
    // Create a minimal draft atom on the backend immediately
    const created = await createAtom({ title: 'Neuer Eintrag', type: 'note' })
    atoms = [created, ...atoms]
    selectedAtom = created
    isNewAtom = true
  }

  async function handleNewSave(id: string, data: AtomUpdate) {
    const updated = await updateAtom(id, data)
    atoms = atoms.map(a => a.id === id ? updated : a)
    selectedAtom = updated
    isNewAtom = false
  }
```

- [ ] **Step 2: Wire "+ Neu" button in the template**

Replace `<button class="btn-primary">+ Neu</button>` with:

```svelte
      <button class="btn-primary" onclick={handleNew}>+ Neu</button>
```

- [ ] **Step 3: Verify in browser**

Click "+ Neu" — a new row "Neuer Eintrag" appears at the top of the list, panel opens. Edit the title, change the type, click Speichern. Row updates. Close the panel. The atom persists across page refreshes (F5).

- [ ] **Step 4: Commit**

```bash
git add frontend/src/routes/+page.svelte
git commit -m "feat: new atom flow — create on click, edit in panel, persist immediately"
```

---

## Task 15: Final Verification + Cleanup

- [ ] **Step 1: Run full test suite**

```bash
make test
```

Expected: `27 passed, 0 failed`

- [ ] **Step 2: Smoke test the full user flow**

1. Open `http://localhost:5173`
2. Click "+ Neu" — new atom appears, panel opens
3. Set title "Meeting vorbereiten", type "Aufgabe", status "Offen", priority "Hoch"
4. Click "Speichern" — row shows status and priority badges
5. Click captured toggle in the row — checkbox turns green
6. Click "Inbox" badge — atom disappears from list (it's now captured)
7. Click "Inbox" badge again to deactivate — atom reappears
8. Click row to open panel — click "Löschen" once (confirm state), then again — atom deleted
9. Run `make backup` — `backups/backup_YYYYMMDD_HHMMSS.sql` file created

- [ ] **Step 3: Commit final state**

```bash
git add -A
git commit -m "feat: Phase 1 complete — full vertical slice, all four atom types, list + panel UI"
```

---

## Checklist gegen Spec

| Anforderung | Task | Status |
|---|---|---|
| Docker Dev + Prod getrennt | 1 | ✓ |
| PostgreSQL Volume (kein Datenverlust) | 1 | ✓ |
| Tägliches Backup | 1 (make backup) | ✓ |
| DB-Modelle: Atom, Person, Project | 4 | ✓ |
| M2M: responsible, participants, projects | 4, 9 | ✓ |
| Soft-Delete überall | 7, 8, 9 | ✓ |
| TDD alle Endpunkte | 6, 7, 8, 9 | ✓ |
| Person: name, photo_url, organizations[] | 4, 7 | ✓ |
| Project: name, color, icon | 4, 8 | ✓ |
| Atom: alle Spec-Felder | 4, 9 | ✓ |
| captured: nur manuell setzbar | 9, 13 | ✓ |
| Filter-Badges (Inbox, heute, überfällig) | 9, 12 | ✓ |
| Frontend: Kompakt-Liste | 12 | ✓ |
| Frontend: Detail-Expand (Pfeil) | 12 | ✓ |
| Frontend: Panel mit allen Feldern | 13 | ✓ |
| Frontend: + Neu Atom anlegen | 14 | ✓ |
| Keine linke Sidebar | 12 | ✓ |
