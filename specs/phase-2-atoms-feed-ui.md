---
name: phase-2-atoms-feed-ui
title: Phase 2 — Atoms-Feed-UI
type: phase
status: implemented
created: 2026-05-01
updated: 2026-05-03
owner: martin
related_prs: ["#2"]
---

# Phase 2 — Atoms-Feed-UI

## Management Summary

Bau das Herzstück der App: eine einspaltige Feed-Ansicht auf `/`, in der Martin neue Atoms in einem Quick-Capture-Feld anlegt und in Kartenform sieht. Soft-Delete per Hover-Button. Keine Metadata-Picker, keine Saved Filters, kein Markdown-Editor — bewusst minimal.

## User Perspective

Aus Sicht Martins:

- `/` zeigt oben ein Texteingabefeld + Typ-Dropdown („Notiz/Aufgabe/Event/Wecker/Referenz") + Anlegen-Button.
- Cmd/Ctrl+Enter im Textfeld sendet ab.
- Neue Atoms erscheinen sofort oben in der Liste (optimistic).
- Jede Karte zeigt Typ-Badge, Inhalt, relative Zeit. Beim Hover erscheint ein Lösch-Button.
- Fehler beim Speichern → Atom verschwindet wieder, Toast unten rechts erklärt warum.

Akzeptanzkriterien (alle erfüllt):

- [x] `make check` grün.
- [x] Atom anlegen, reload → bleibt sichtbar.
- [x] Atom löschen → verschwindet aus Liste, `deleted_at` in DB gesetzt.
- [x] Backend nicht erreichbar → Fehlermeldung statt leerer Seite.

## Technical Details

- API-Client `frontend/src/lib/api/client.ts` mit `apiFetch` + `listAtoms`/`createAtom`/`updateAtom`/`deleteAtom`.
- OpenAPI-Types via `npm run generate:api` aus laufendem Backend.
- Komponenten: `QuickCapture`, `AtomCard`, `AtomList`. Reine Props, keine globalen Stores.
- Optimistisches Insert/Delete mit Rollback bei Fehler.
- `vitest.config.ts`: `$lib`-Alias und `conditions: ['browser']` für Svelte 5 in jsdom.
- e2e mit Playwright und `page.route()`-Mocking — kein echtes Backend in CI nötig.

## Open Questions

—

## Roast Notes

Backfilled. Im Nachgang aufgefallen:

- Slug wird Client-seitig generiert (`a-YYYY-MM-DD-<rand>`), obwohl die Spec im Backend ihn auch hätte erzeugen können. Bewusste Entscheidung für Konsistenz mit Phase 1, in der `AtomCreate.slug` als Pflichtfeld definiert wurde.
- Playwright in CI scheiterte zunächst, weil dev-Server-Proxy `/api` zu nicht existierendem Backend wollte → behoben durch `page.route()`-Mocking.
- Migration in frischer DB lief nicht via `make migrate` (Docker-Build-Fehler wegen `../README.md`-Pfad), wurde nativ ausgeführt — tracking nötig, kein Spec-relevantes Detail.

## Implementation Log

- 2026-05-03 — Umstieg von `vite preview` (4173) auf dev-Server (5173) in `playwright.config.ts`, weil nur dev-Server den `/api`-Proxy hat.
- 2026-05-03 — CI-Fix: e2e-Tests von echten API-Calls auf `page.route()`-Mocks umgestellt, da kein Backend im CI-Job läuft.

## Final Implementation

- Atoms-Feed mit Quick-Capture und Karten-Liste auf `/`.
- 21 Vitest-Unit-Tests + 4 Playwright-e2e-Tests, alle grün.
- 33 Backend-Tests weiterhin grün.
- PR: [#2](https://github.com/martinbaerwolff/atoms/pull/2).
