# Atoms — Claude Code instructions

This file is loaded automatically at the start of every Claude session in this repo. Read it once, follow the rules, and check the linked skill files for the workflow you need.

---

## What this project is

**Atoms** is Martin's personal Second Brain. The atoms (notes, tasks, thoughts, decisions, links) are the central unit; people/meetings/projects are the connective tissue. Manual-first, AI-second — the app itself has no auto-magic, but you (Claude) can hit the database directly to run skills and analyses.

UI language: **German**. Code, identifiers, comments, commit messages, PR descriptions, logs: **English**.

Domain vocabulary (DE → EN):
- Aufgabe → `task` · Notiz → `note` · Gedanke → `thought` · Beschluss → `decision` · Link → `link`
- Inbox → `inbox=TRUE`
- Wecker → `reminder`
- Liegt bei → `assigned_to`
- Beteiligte → atom_persons (n:m)

---

## Hard rules

1. **TDD is mandatory.** Every new endpoint, service, or component starts with a failing test. No "I'll add tests later." See `skills/tdd.md`.
2. **`make check` must pass before commit.** That runs lint + typecheck + tests. Pre-commit hooks enforce this.
3. **Never `--no-verify`, never force-push, never `git reset --hard`** without an explicit instruction from Martin in this session.
4. **Branch per feature → PR → green CI → merge.** No direct commits to `main`.
5. **No backwards-compat shims, no premature abstraction, no UI dekoration.** See memory: minimalismus.
6. **Soft-delete only.** Never `DELETE FROM`; always set `deleted_at` and filter it out in views/queries.
7. **One DB session per request.** Use the `get_session` dependency; never instantiate engines/sessions in routers.
8. **Schema changes go through Alembic.** Never edit production data without a migration script (when in cloud).
9. **Spec-first.** Every feature, bug, and phase begins as a spec in `specs/`. Trivial fixes (≤ 10 LoC, clear cause) are exempt. See `specs/README.md`.

---

## Spec-driven development

Each feature/bug/phase has exactly one Markdown file in `specs/<kebab-name>.md` that travels through the lifecycle: `ideated` → `planned` → `roasted` → `in_implementation` → `implemented` (or `abandoned`). Source of truth for *what is being built and why* is the spec — not the commit message or PR description.

Four slash commands drive the lifecycle:

| Command | Required model | What it does |
|---|---|---|
| `/ideate-spec <description>` | **Opus** | Creates a new spec at `status: ideated`, picks a kebab-case name, fills in the management summary. |
| `/plan-spec <name>` | **Opus** | Fleshes out User Perspective + Technical Details, sets `status: planned`. |
| `/roast-spec <name>` | **Opus** | Critiques the spec (≥ 5 points), records resolutions, sets `status: roasted`. |
| `/implement-spec <name>` | **Sonnet** | Builds it — branch, code, tests, PR — and logs decisions/deviations in the spec. |

Each command starts with a hard model-gate: if the wrong model family is active, the skill stops immediately and asks the user to switch via `/model`. There is no programmatic model switch in Claude Code.

Spec-only commands (`ideate`/`plan`/`roast`) each open their own PR so discussion lives in PR comments. `implement-spec` opens a single PR containing both the code and the spec updates (Implementation Log, Final Implementation, status, related_prs).

See `specs/README.md` for frontmatter schema and `specs/_template.md` for the empty starting point. The meta-spec `specs/spec-driven-development.md` documents this system itself.

---

## Stack & layout

| Layer | Tech |
|---|---|
| Backend | Python 3.13, FastAPI, SQLAlchemy 2 async, Alembic, Pydantic v2, structlog |
| DB | PostgreSQL 17 (local: `db` service in docker compose) |
| Frontend | SvelteKit + adapter-static (SPA), Svelte 5 runes, TS strict, Tailwind v4, TipTap (later) |
| Tests | pytest + httpx + testcontainers / vitest + Playwright |
| Lint | ruff, mypy strict, eslint, prettier, svelte-check |
| Runtime | Docker Compose locally; Hetzner+Cloudflare+Tailscale in Phase 5 |

```
atoms/
├── CLAUDE.md                 # ← you are here
├── Makefile                  # `make help` lists everything
├── docker-compose.yml        # postgres + backend + frontend (dev)
├── .claude/                  # settings, custom agents, slash commands
├── backend/
│   ├── app/                  # FastAPI app (main, db, settings, models, services, routers)
│   ├── tests/                # pytest (unit + integration)
│   └── pyproject.toml        # ruff, mypy, pytest config lives here
├── frontend/
│   ├── src/
│   │   ├── routes/           # /, /people, /meetings, /projects
│   │   ├── lib/              # components, stores, api, editor
│   │   └── app.css           # Tailwind v4 + IBM Plex + Petrol theme
│   └── tests/                # vitest (unit) + Playwright (e2e)
├── infra/                    # Caddyfile, Cloudflare tunnel, ansible (cloud phase)
└── skills/                   # workflow guides, see below
```

---

## Daily commands

```bash
make help            # list everything
make dev             # docker compose up (postgres + backend + frontend)
make psql            # open psql in compose db
make migrate         # alembic upgrade head
make makemigration name=add_atoms_table
make fresh           # nuke db volume + recreate + migrate (DESTRUCTIVE)
make test            # backend (pytest) + frontend (vitest) — fast
make test-e2e        # Playwright (slower, needs services)
make lint            # ruff + eslint + prettier --check + svelte-check
make format          # autofix
make check           # CI equivalent locally
```

Connection string (local dev): `postgresql://atoms:atoms@localhost:5432/atoms`

---

## API routes (Phase 1+)

```
GET/POST   /atoms              list + create
GET/PATCH/DELETE /atoms/{id}   get, update, soft-delete
GET        /atoms?q=...        fulltext search (German tsvector)
GET/POST   /persons            list + create
GET/PATCH/DELETE /persons/{id}
GET/POST   /meetings           list + create (participant_ids in body)
GET/PATCH/DELETE /meetings/{id}
GET/POST   /projects
GET/PATCH/DELETE /projects/{id}
GET/POST   /saved-filters
GET/PATCH/DELETE /saved-filters/{id}
GET        /views/inbox        atoms where inbox=TRUE
GET        /health             DB ping
```

## Standard views (Postgres VIEWs — created in migration 0001)

- `v_inbox` — atoms with `inbox=TRUE`, not soft-deleted
- `v_overdue_tasks` — tasks past deadline, status not in `done|cancelled`
- `v_upcoming_reminders` — atoms with `reminder` in future, not soft-deleted
- `v_open_tasks` — open tasks sorted by priority then created_at

---

## ID conventions

- Internal PK: `UUIDv7` (time-sortable). Generated in DB or in Python via `uuid7`.
- Human-readable `slug TEXT UNIQUE`:
  - atoms: `a-YYYY-MM-DD-NNN` (sequential within day)
  - persons: `lastname-firstname` lowercased
  - meetings: `m-YYYY-MM-DD-shortname`
  - projects: any short kebab-case identifier
- All timestamps: `TIMESTAMPTZ`, ISO 8601 UTC at the API boundary.

---

## Domain enums (must stay in sync between DB + Pydantic + frontend)

- atom type: `note | task | thought | decision | link`
- task status: `open | in_progress | waiting | done | cancelled`
- task priority: `low | medium | high | critical`
- project status: `active | paused | done | archived`

---

## Skills (open these before starting common tasks)

- `skills/tdd.md` — the test-first loop in detail
- `skills/db.md` — connecting to the DB, writing safe queries
- `skills/workflows.md` — Inbox triage, Meeting → Atoms, Weekly review

---

## Phase status

- [Phase 0 — tooling skeleton](specs/phase-0-tooling-skeleton.md) ✅
- [Phase 1 — DB schema + CRUD](specs/phase-1-db-schema-and-crud.md) ✅
- [Phase 2 — Atoms feed UI](specs/phase-2-atoms-feed-ui.md) ✅
- [Phase 3 — metadata pickers + saved filters](specs/phase-3-metadata-pickers.md) (ideated)
- Phase 4 — people/meetings/projects table feeds + drawers (no spec yet)
- Phase 5 — cloud deployment (Hetzner + Cloudflare + Tailscale)

Always check `git log --oneline -20` and `make ps` at session start to understand the actual state — this file can drift.
