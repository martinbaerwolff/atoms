# Atoms

A personal "Second Brain" — atoms (notes, tasks, thoughts, decisions, links) with people, meetings and projects woven through. Manual-first, AI-second.

## Stack

- **Backend:** Python 3.13, FastAPI, SQLAlchemy 2 async, Alembic, Pydantic v2.
- **Database:** PostgreSQL 17.
- **Frontend:** SvelteKit (static adapter, SPA), TypeScript strict, Tailwind v4, TipTap with markdown plugin.
- **Tests:** pytest + testcontainers (backend), vitest + Playwright (frontend).
- **Lint/Format:** ruff, mypy strict, eslint, prettier, svelte-check, pre-commit.
- **Local runtime:** Docker Compose.
- **Cloud (later):** Hetzner + Cloudflare Tunnel/Access + Tailscale.

## Quickstart

```bash
cp .env.example .env
make install        # uv sync backend, npm install frontend, pre-commit hooks
make dev            # docker compose up -- postgres + backend + frontend
```

Open [http://localhost:5173](http://localhost:5173) for the frontend, [http://localhost:8000/docs](http://localhost:8000/docs) for the API.

## Common commands

| Command | What it does |
|---|---|
| `make dev` | Boot full stack (compose up) |
| `make down` | Stop the stack |
| `make psql` | Open `psql` in the compose Postgres |
| `make migrate` | Apply Alembic migrations |
| `make makemigration name=...` | Autogenerate a migration |
| `make fresh` | Drop DB volume, recreate, migrate (destructive) |
| `make test` | Run backend + frontend unit tests |
| `make test-e2e` | Playwright E2E tests |
| `make lint` | Lint everything (no autofix) |
| `make format` | Format everything |
| `make check` | Local CI equivalent (lint + typecheck + tests) |

## Project layout

See `CLAUDE.md` for the canonical map and the conventions Claude Code follows when working on this repo.
