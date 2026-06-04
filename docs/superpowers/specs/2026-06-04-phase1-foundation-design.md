# Atoms — Phase 1: Foundation Design

**Datum:** 2026-06-04
**Status:** Freigegeben
**Scope:** Vollständiger vertikaler Schnitt — Datenmodell, Backend-API, Frontend-UI

---

## Überblick

Atoms ist eine persönliche Mission-Control-App für eine einzelne Nutzerperson. Vier gleichwertige Inhaltstypen (Notiz, Gedanke, Aufgabe, Entscheidung) leben in einer gemeinsamen Liste. Das zentrale Konzept ist das `captured`-Flag: der Unterschied zwischen "irgendwo notiert" und "wirklich verarbeitet".

Phase 1 liefert einen vollständig nutzbaren vertikalen Schnitt: Datenbank → API → UI. Alle vier Typen sind von Anfang an in einer gemeinsamen Liste vorhanden — das ist die zentrale These der App.

---

## Infrastruktur

**Stack:** FastAPI (Python), PostgreSQL, SvelteKit, Docker Compose.

**Umgebungen:** Dev und Prod sind vollständig getrennt — eigene Docker-Compose-Konfigurationen, eigene Datenbanken, keine Vermischung. `make dev` startet die Entwicklungsumgebung, `make start` die Produktionsumgebung.

**Datenpersistenz:** Die PostgreSQL-Datenbank liegt in einem Docker-Volume auf der lokalen Festplatte — kein Datenverlust beim Neustart oder Rebuild von Containern.

**Backup:** Tägliches automatisches Backup der Datenbank als SQL-Dump in einen lokalen Ordner (`./backups/`). Dieser Ordner kann in Synology Drive gelegt werden. Wiederherstellung: Dump zurückspielen, fertig.

**Portabilität:** Neuer Rechner = Git-Repo klonen + Docker starten + Backup einspielen.

**Secrets:** Alle Zugangsdaten in `.env`-Dateien, nie im Git.

---

## Datenmodell

### Atoms

Die zentrale Tabelle. Alle vier Typen (`note`, `thought`, `task`, `decision`) liegen in einer Tabelle — kein getrenntes Schema pro Typ.

| Feld | Typ | Pflicht | Anmerkung |
|---|---|---|---|
| id | UUID | ja | Primary Key |
| title | Text | ja | |
| content | Text (Markdown) | nein | |
| type | Enum | ja | `note` / `thought` / `task` / `decision` |
| captured | Boolean | ja | Default: `false`. Nur manuell durch den Nutzer setzbar — nie automatisch |
| status | Enum | nein | `open` / `in_progress` / `blocked` / `done` / `cancelled` — nur bei `task` relevant |
| priority | Enum | nein | `high` / `medium` / `low` — nur bei `task` |
| complexity | Enum | nein | `deep` / `shallow` / `routine` — nur bei `task` |
| deadline_date | Timestamp | nein | nur bei `task` |
| alarm_date | Timestamp | nein | nur bei `task` |
| source_url | Text | nein | alle Typen |
| created_at | Timestamp | ja | automatisch |
| updated_at | Timestamp | ja | automatisch, bei jeder Änderung |
| deleted_at | Timestamp | nein | Soft-Delete: gesetzter Wert = gelöscht |

**Indizes:** `type`, `captured`, `status`, `deadline_date`, `created_at`, `deleted_at`

### Persons

Wiederverwendbare Personen-Einträge.

| Feld | Typ | Pflicht | Anmerkung |
|---|---|---|---|
| id | UUID | ja | |
| name | Text | ja | |
| photo_url | Text | nein | Link zu einem Bild |
| organizations | Text[] | nein | Array von Organisationsnamen (kein eigenes Entity) |
| created_at | Timestamp | ja | |
| updated_at | Timestamp | ja | |
| deleted_at | Timestamp | nein | Soft-Delete |

### Projects

| Feld | Typ | Pflicht | Anmerkung |
|---|---|---|---|
| id | UUID | ja | |
| name | Text | ja | |
| color | Text | nein | Hex-Farbcode, z.B. `#3B7A57` |
| icon | Text | nein | Emoji oder Icon-Bezeichner |
| created_at | Timestamp | ja | |
| updated_at | Timestamp | ja | |
| deleted_at | Timestamp | nein | Soft-Delete |

### Relationen

Alle drei als eigene Join-Tabellen (M2M):

- **atom_responsible** — Atom ↔ Person (Verantwortlich). Technisch M2M, in der UI vorerst Einfachauswahl. Vorbereitung für spätere Mehrfachzuständigkeit.
- **atom_participants** — Atom ↔ Person (Beteiligt). M2M, Mehrfachauswahl.
- **atom_projects** — Atom ↔ Project. M2M, Mehrfachauswahl.

### Nicht in Phase 1

- Anhänge (Phase 4)
- Versionshistorie / Snapshots (Phase 3)
- Gespeicherte Filtersets als DB-Entität (Phase 2) — die vordefinierten Badges ("Heute erstellt" etc.) sind in Phase 1 hartcodiert im Frontend

---

## Backend-API

**Framework:** FastAPI mit Pydantic-Schemas, SQLAlchemy ORM, Alembic für Migrationen.

### Endpunkte

**Atoms**
- `GET /atoms` — Liste; Query-Parameter: `type`, `captured`, `deleted` (default: false)
- `POST /atoms` — Neues Atom anlegen
- `GET /atoms/{id}` — Einzelnes Atom mit allen Relationen
- `PATCH /atoms/{id}` — Felder aktualisieren (partial update)
- `DELETE /atoms/{id}` — Soft-Delete (setzt `deleted_at`)

**Persons**
- `GET /persons` — Liste aller aktiven Personen
- `POST /persons`
- `GET /persons/{id}`
- `PATCH /persons/{id}`
- `DELETE /persons/{id}` — Soft-Delete

**Projects**
- `GET /projects` — Liste aller aktiven Projekte
- `POST /projects`
- `GET /projects/{id}`
- `PATCH /projects/{id}`
- `DELETE /projects/{id}` — Soft-Delete

### Relationen in der API

Beim Erstellen/Aktualisieren eines Atoms werden Relationen als ID-Listen übergeben:
```json
{
  "responsible_ids": ["uuid1"],
  "participant_ids": ["uuid2", "uuid3"],
  "project_ids": ["uuid4"]
}
```

`GET /atoms/{id}` gibt aufgelöste Objekte zurück (kein separater Request nötig).

### Regeln

- `captured` kann über die API gesetzt werden, aber es liegt in der Verantwortung des Frontends, das nur auf explizite Nutzer-Aktion hin zu tun — nie automatisch
- Gelöschte Einträge (`deleted_at` gesetzt) werden in keiner Liste zurückgegeben, außer `?deleted=true`
- Alle Fehler als JSON mit `detail`-Feld

### Testing

TDD: Jeder Endpunkt bekommt Tests bevor die Implementierung geschrieben wird. Tests laufen gegen eine echte Test-Datenbank (kein Mocking). Mindestens: Happy Path + Fehlerfall + Soft-Delete-Verhalten.

---

## Frontend-UI

**Framework:** SvelteKit (SSR deaktiviert, reine SPA). API-Kommunikation über einen zentralen `api`-Client.

### Layout

Keine linke Navigationsleiste. Die gesamte App ist eine einzige Hauptansicht:

```
┌─────────────────────────────────────────────────────────────────┐
│  ⬡ Atoms                              [Kompakt][Detail] [+ Neu] │
├─────────────────────────────────────────────────────────────────┤
│  [Heute erstellt] [Heute geändert] [Überfällig] [Inbox]         │
├──────────────────┬──────────┬──────┬──────┬──────┬──────────────┤
│  TITEL / INHALT  │  STATUS  │ PRIO │ VERANTW │ PROJEKTE │ CAPT  │
├──────────────────┼──────────┼──────┼─────────┼──────────┼───────┤
│  > ◎ Titel...    │ offen    │ hoch │  (MA)   │ CRM      │  □    │
│  v □ Titel...    │          │      │  (FR)   │ Infra    │  ✓    │
│    Textvorschau...                                               │
├──────────────────┴──────────┴──────┴─────────┴──────────┴───────┤
```

Wenn Panel offen:
```
┌──────────────────────────────┬──────────────────────────────────┐
│  Liste (schmaler)            │  Panel                           │
│                              │  Titel (editierbar)              │
│  > ◎ Titel...                │  Inhalt (Markdown, editierbar)   │
│  [ausgewählt, grüner Rand]   │                                  │
│                              │  KOMPAKT-FELDER                  │
│                              │  Verantwortlich, Beteiligt,      │
│                              │  Projekte, Captured              │
│                              │                                  │
│                              │  NUR PANEL                       │
│                              │  Status, Priorität, Komplexität, │
│                              │  Fälligkeit, Wecker, Quelle      │
│                              │  Erstellt, Geändert (nur lesend) │
└──────────────────────────────┴──────────────────────────────────┘
```

### Anzeigeebenen

**Kompakt:** Eine Zeile pro Atom. Sichtbar: Typ-Icon, Titel, Status (nur Task), Priorität (nur Task), Fälligkeit (nur Task), Verantwortlich-Avatar, Projekt-Badges, Captured-Checkbox.

**Detail:** Zeile aufgeklappt via ">" Pfeil. Zusätzlich: erste Zeilen des Inhaltsfeldes als Vorschau. Toggle oben rechts klappt alle Zeilen gleichzeitig auf/zu.

**Panel:** Öffnet sich bei Zeilenklick. Alle Felder editierbar. Zwei Abschnitte: "Kompakt-Felder" und "Nur Panel".

### Typ-Icons

Jeder Typ bekommt ein eigenes farbiges Icon:
- `note` — Dokument-Icon, blaugrau
- `thought` — Kreis/Idee-Icon, lila
- `task` — Checkbox-Icon, grün (Akzentfarbe)
- `decision` — Waage/Stern-Icon, orange

### Filter-Badges (Phase 1, hardcodiert)

- **Inbox** — `captured = false`
- **Heute erstellt** — `created_at >= heute 00:00`
- **Heute geändert** — `updated_at >= heute 00:00`
- **Überfällig** — `type = task AND deadline_date < jetzt AND status NOT IN (done, cancelled)`

Ein Badge kann aktiv sein (grüner Hintergrund). Kein Badge aktiv = alle Einträge sichtbar.

### Neuer Eintrag

"+ Neu" Button oben rechts öffnet das Panel mit leerem Formular. Typ-Auswahl im Panel. Speichern legt den Eintrag an und zeigt ihn in der Liste.

### Löschen

Soft-Delete. Eintrag verschwindet aus der Liste. Kein Papierkorb in Phase 1.

### Design-Sprache

- Typografie: klare serifenlose Schrift (Inter oder ähnlich)
- Farben: heller Hintergrund, ruhige Grautöne, ein dezenter Grünton als Akzentfarbe
- Viel Weißraum, keine bunten Flächen
- Kein Enterprise-Look, kein Consumer-Spielzeug-Look

---

## Nicht in Phase 1

Folgendes ist bewusst ausgelassen und kommt in späteren Phasen:

| Feature | Phase |
|---|---|
| Filterzeile unter Spaltenköpfen (Dropdowns) | 2 |
| Gespeicherte Filtersets (nutzerdefiniert) | 2 |
| Sortierung per Spaltenklick | 2 |
| Spalten ein-/ausblenden | 2 |
| Mehrfachauswahl + Sammelbearbeitung | 3 |
| Versionshistorie | 3 |
| Anhänge | 4 |
| Server-Deployment (Provider offen) | 5 |

---

## Phasen-Übersicht (gesamt)

| Phase | Inhalt |
|---|---|
| 1 | Foundation: Datenmodell, API, Listen-UI, Panel (dieser Spec) |
| 2 | Filters: Filterzeile, gespeicherte Filtersets, Sortierung, Spalten |
| 3 | Power: Mehrfachauswahl, Sammelbearbeitung, Versionshistorie |
| 4 | Attachments: Datei-Anhänge |
| 5 | Deploy: Self-Hosted Server (Provider wird in Phase 5 entschieden) |

---

## Begriffe: UI (Deutsch) → Code / DB (Englisch)

| UI | Code/DB |
|---|---|
| Notiz | note |
| Gedanke | thought |
| Aufgabe | task |
| Entscheidung | decision |
| Erfasst | captured |
| Verantwortlich | responsible |
| Beteiligt | participant |
| Projekt | project |
| Offen | open |
| Läuft | in_progress |
| Blockiert | blocked |
| Erledigt | done |
| Abgebrochen | cancelled |
| Fälligkeit | deadline_date |
| Wecker | alarm_date |
| Priorität | priority |
| Komplexität | complexity |
| Tiefe Arbeit | deep |
| Oberflächlich | shallow |
| Routine | routine |
| Quelle | source_url |
| Erstellt | created_at |
| Geändert | updated_at |
| Inbox | inbox (captured=false) |
