---
name: phase-3-metadata-pickers
title: Phase 3 — Metadata-Picker + Saved Filters
type: phase
status: ideated
created: 2026-05-03
updated: 2026-05-03
owner: martin
related_prs: []
---

# Phase 3 — Metadata-Picker + Saved Filters

## Management Summary

Erweitere den Atoms-Feed aus Phase 2 um die Möglichkeit, Atoms beim Anlegen oder nachträglich mit Metadaten zu versehen — Personen, Projekt, Meeting, Deadline, Wecker, Status, Priorität — und nach all diesen Dimensionen zu filtern. Filter, die Martin häufig braucht, lassen sich speichern und in der Sidebar wiederverwenden.

## User Perspective

_(grobe Stichpunkte — wird in `/plan-spec` ausformuliert)_

- Inline-Picker im Quick-Capture und Detail-Drawer (ohne dass das Hauptlayout geändert werden muss).
- Filter-Leiste über dem Feed: Type, Status, Priority, Personen, Projekt, Datumsrange.
- Saved Filter: Filter-Setting unter Namen speichern, in Sidebar verlinkt, ein Klick → angewendet.
- Inbox-View nutzt das Filter-System (`inbox=TRUE`) statt einer separaten Route.

## Technical Details

_(noch nicht gefüllt — wird in `/plan-spec`)_

## Open Questions

- TipTap einführen oder bei Textarea bleiben?
- Filter-State im URL kodieren (deep-linkable) oder im LocalStorage?
- Saved Filters: pure Frontend-Persistenz oder über `/saved-filters`-API?

## Roast Notes

_(wird von `/roast-spec` befüllt, sobald Plan-Phase abgeschlossen ist)_

## Implementation Log

—

## Final Implementation

—
