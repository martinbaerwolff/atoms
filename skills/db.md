# Skill: Database access

## Local (dev)

Postgres runs as the `db` service in docker compose. Bring the stack up first:

```bash
make dev      # backgrounded? use `make dev` in another shell, or `docker compose up -d`
```

Connect:

```bash
make psql                                                # easiest
docker compose exec db psql -U atoms -d atoms
psql postgresql://atoms:atoms@localhost:5432/atoms       # from host, after compose is up
```

DSN (host): `postgresql://atoms:atoms@localhost:5432/atoms`
DSN (containers): `postgresql+asyncpg://atoms:atoms@db:5432/atoms`

## Cloud (Phase 5+, NOT YET ACTIVE)

When the cloud stack lands, the database is on Hetzner, only reachable through Tailscale. There will be three roles:

- `atoms_app` — owner used by FastAPI.
- `atoms_claude_rw` — your read/write account for ad-hoc edits via psql.
- `atoms_claude_ro` — for read-only subagents (analytical queries that shouldn't risk a write).

Connection strings will be added here when Phase 5 starts.

## Standard views (defined in initial migration once Phase 1 lands)

```sql
SELECT * FROM v_inbox;
SELECT * FROM v_overdue_tasks;
SELECT * FROM v_upcoming_reminders;
SELECT * FROM v_open_tasks;
```

All four hide `deleted_at IS NOT NULL` rows — never UNION them with raw `atoms`.

## Safe-query checklist

- Read-only investigation? Use a transaction with `BEGIN; ...; ROLLBACK;` so you can't fat-finger an UPDATE.
- Modifying data? Run a `SELECT` first that returns the rows you intend to touch. Eyeball them. Then run the UPDATE/DELETE in the same transaction.
- Schema change? Always through Alembic (`make makemigration name=...`), never raw `ALTER TABLE`.
- Don't `TRUNCATE` (use `make fresh` if you really want a blank slate locally).
