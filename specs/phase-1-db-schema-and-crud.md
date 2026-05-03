---
name: phase-1-db-schema-and-crud
title: Phase 1 — DB-Schema + CRUD
type: phase
status: implemented
created: 2026-04-20
updated: 2026-05-03
owner: martin
related_prs: ["#1"]
---

# Phase 1 — DB-Schema + CRUD

## Management Summary

Lege das vollständige Datenmodell für Atoms an (atoms, persons, meetings, projects, saved_filters, atom_persons-Verknüpfung) und exponiere CRUD-Endpoints für jede Ressource. Soft-Delete überall, fünf Standard-Views (`v_inbox`, `v_overdue_tasks`, `v_upcoming_reminders`, `v_open_tasks`). Voll TDD-getestet.

## User Perspective

Noch keine UI in dieser Phase — der Wert ist die API. Martin kann via `curl` oder OpenAPI-Docs (`/docs`) Atoms anlegen, lesen, aktualisieren und (soft-)löschen, ebenso für die anderen Ressourcen.

## Technical Details

- SQLAlchemy 2 async + Alembic.
- UUIDv7 als PK (zeitsortiert), `slug TEXT UNIQUE` als zweiter Schlüssel.
- Enums hart in DB + Pydantic + Frontend-Types gehalten.
- `created_at`, `updated_at`, `deleted_at` (TIMESTAMPTZ) in jeder Tabelle.
- Migration `0001_initial_schema.py` enthält Tabellen, Indizes, Views, Trigger für `updated_at`.
- Tests: pytest + testcontainers für Integrationstests gegen echtes Postgres.
- Out-of-Scope: Frontend-UI, Auth, Multi-User.

## Open Questions

—

## Roast Notes

Backfilled — kein expliziter Roast vor Implementierung. Im Nachgang aufgefallen: Domain-Vokabular driftet leicht (Plan sagte `event/reference`, CLAUDE.md sagt `thought/decision/link`). Wird in einer späteren Spec sauber zusammengeführt.

## Implementation Log

—

## Final Implementation

- 33 Backend-Tests grün, vollständige CRUD-API für alle Ressourcen.
- Alembic-Migration 0001 erzeugt sauberes Schema von Null.
- Alle Views + Indizes wie in CLAUDE.md spezifiziert.
- PR: [#1](https://github.com/martinbaerwolff/atoms/pull/1).
