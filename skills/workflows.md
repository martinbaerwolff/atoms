# Skill: Common workflows

## Inbox triage

Goal: visit each `inbox=TRUE` atom, decide its real type/project/people/priority, set `inbox=FALSE`.

```sql
SELECT id, slug, type, content, created_at FROM v_inbox ORDER BY created_at DESC;
```

For each row:
- Decide: keep as `note`? Convert to `task` (set status=`open` and a priority)? Convert to `decision`?
- Attach project / meeting / persons via the relation tables.
- Set `inbox=FALSE`.

Don't bulk-process — Martin will want to see each one.

## Meeting → Atoms

When Martin pastes meeting notes:

1. Create a `meetings` row (slug `m-YYYY-MM-DD-shortname`).
2. Add `meeting_participants` rows for everyone present.
3. Walk the notes. For every action item: insert an atom with `type='task'`, link `meeting_id`, set `assigned_to` if the notes say "Thomas: …".
4. For decisions: `type='decision'`, link `meeting_id`.
5. The raw notes themselves go in **one** atom with `type='note'` linked to the meeting.

## Weekly review

```sql
-- Overdue tasks
SELECT slug, content, deadline, deadline_hard FROM v_overdue_tasks;

-- Open decisions sitting in inbox (suggests they were dropped in but never categorized)
SELECT slug, content FROM v_inbox WHERE type = 'decision';

-- Stale projects
SELECT id, name, status, updated_at FROM projects
WHERE status = 'active' AND deleted_at IS NULL
  AND updated_at < now() - interval '14 days'
ORDER BY updated_at;
```

Read these out, ask Martin which to act on, batch the updates in a single transaction.

## Phase-5 only: incident workflow

If something looks wrong on the live DB:
1. `psql` as `atoms_claude_ro` first to investigate (read-only).
2. If a write is needed, switch to `atoms_claude_rw` *and* wrap in a transaction.
3. Document the change in a markdown doc under `docs/incidents/` after the fact.
