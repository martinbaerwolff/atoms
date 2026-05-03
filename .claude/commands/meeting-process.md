---
description: Turn pasted meeting notes into structured atoms (meeting + tasks + decisions + raw note)
---

Martin will paste meeting notes after invoking this command. Your job:

1. Ask Martin (only if missing): meeting title, date, expected duration, project, attendees.
2. Insert one row into `meetings` (slug `m-YYYY-MM-DD-<shortname>`).
3. Insert `meeting_participants` for every attendee. If a person doesn't exist yet, create them and confirm with Martin first.
4. Walk the notes:
   - Action items ("→ Thomas: ..." / "Follow-up: ...") → atoms with `type='task'`, `status='open'`, `assigned_to=<person_id>` if implied, `meeting_id=<id>`.
   - Decisions ("Beschluss: ...") → atoms with `type='decision'`, `meeting_id=<id>`.
   - Everything else: ONE atom with `type='note'` containing the full notes verbatim, `meeting_id=<id>`.
5. All inserts in **one transaction** so a parser bug rolls back cleanly.
6. Print a summary of what was created (counts by type + slugs).

Don't skip the raw-note atom — it's the source of truth.
