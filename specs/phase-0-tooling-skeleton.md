---
name: phase-0-tooling-skeleton
title: Phase 0 — Tooling-Skelett
type: phase
status: implemented
created: 2026-04-15
updated: 2026-05-03
owner: martin
related_prs: []
---

# Phase 0 — Tooling-Skelett

## Management Summary

Lege das technische Fundament für Atoms an: Backend-Skelett (FastAPI), Frontend-Skelett (SvelteKit), Docker-Compose für lokale Entwicklung, Lint/Format/Test-Setup, Pre-Commit-Hooks. Keine fachliche Logik — nur die Werkzeugkette, sodass ab Phase 1 jede Änderung CI-fähig getestet werden kann.

## User Perspective

Aus Sicht von Martin: `make install && make dev` reicht, um die App lokal hochzufahren. `make check` ersetzt CI lokal, `make test` läuft schnell. Pre-Commit verhindert, dass schlechter Code überhaupt eingecheckt wird.

## Technical Details

- Backend: Python 3.13, FastAPI, uvicorn, uv als Package-Manager, ruff + mypy strict.
- Frontend: SvelteKit (static-adapter, SPA), Svelte 5 runes, TS strict, Tailwind v4, eslint + prettier + svelte-check.
- DB: Postgres 17 als Docker-Service, noch ohne Schema.
- `Makefile` mit Standard-Targets (`dev`, `test`, `lint`, `check`, `migrate`).
- `.github/workflows/ci.yml` mit Backend- und Frontend-Jobs.
- Out-of-Scope: Atoms-Modell, API-Routen, UI — kommt in Phase 1+.

## Open Questions

—

## Roast Notes

Backfilled — kein Roast vor Implementierung. Im Nachgang keine Mängel aufgefallen, die nicht in späteren Phasen behoben wurden.

## Implementation Log

—

## Final Implementation

- Backend, Frontend und DB fahren via `make dev` hoch.
- `make check` deckt Lint + Typecheck + Tests beider Seiten ab.
- CI grün auf erstem Commit.
- Verbleibender PR: initialer Commit, kein eigener PR (vor Spec-System angelegt).
