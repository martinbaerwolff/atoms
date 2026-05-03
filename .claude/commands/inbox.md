---
description: Show all atoms currently in the inbox
---

You're being asked to surface every atom with `inbox=TRUE` so Martin can triage them.

1. Make sure docker compose is up: `docker compose ps`. If `db` isn't running, ask Martin to `make dev` first.
2. Use the `db-query` subagent to fetch from `v_inbox`:
   - `SELECT slug, type, content, project_id, created_at FROM v_inbox ORDER BY created_at DESC LIMIT 100;`
3. Print a compact summary, grouped by `type`. For each: slug · short content excerpt (first 80 chars) · age (relative).
4. Don't propose changes. Just show. Triage is a separate workflow (`skills/workflows.md`).
