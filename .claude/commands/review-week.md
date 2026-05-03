---
description: Weekly review — overdue tasks, dropped decisions, stale projects
---

Use the `db-query` subagent and run the queries from `skills/workflows.md` "Weekly review" section. Then:

1. **Overdue tasks** — list each, ask Martin which to reschedule, mark done, or escalate.
2. **Dropped decisions** — atoms with `type='decision'` still in inbox. Surface them; they're decisions that never got categorized.
3. **Stale projects** — `status='active'` but not touched in 14 days. Suggest Martin pause or archive.

Output format: three sections, max 10 items each. For each item: slug + content excerpt + suggested action.

Don't act on any of them. Hand the list back to Martin.
