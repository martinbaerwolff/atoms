---
description: Füllt User Perspective und Technical Details einer Spec aus, setzt Status auf `planned`
---

# /plan-spec

Du sollst eine bestehende Spec von `ideated` auf `planned` heben, indem du User Perspective und Technical Details voll ausformulierst.

## 1. Modell-Gate (BLOCKING)

Lies die „You are powered by"-Zeile. Wenn sie **nicht** `Opus` enthält:

> **STOP.** Antworte ausschließlich mit:
>
> „Dieser Skill braucht **Opus** für sorgfältiges Planen (gerade läuft `<aktuelles-modell>`). Bitte mit `/model claude-opus-4-7` wechseln und `/plan-spec <name>` neu aufrufen."
>
> Beende den Turn.

## 2. Spec laden + validieren

- Argument hinter `/plan-spec` ist der Spec-Name (kebab-case, ohne `.md`). Wenn leer: per AskUserQuestion fragen oder die zuletzt geänderte Spec im Status `ideated`/`planned` vorschlagen.
- Lies `specs/<name>.md`. Wenn nicht existent: STOP mit Hinweis auf `/ideate-spec`.
- Prüfe `status` im Frontmatter:
  - `ideated` → ok, normaler Lauf.
  - `planned` → idempotent, ok (Re-Plan).
  - alles andere → STOP mit Erklärung („Spec ist bereits roasted/in_implementation/implemented — ändere sie nicht ohne Grund").

## 3. Codebase-Exploration (wenn relevant)

Wenn die Spec Code im Repo berührt (Indizien: nennt FastAPI-Routen, Komponenten, Migrations etc.): launche **1–3 Explore-Subagenten parallel** um relevante Architektur, bestehende Muster und potenziell wiederverwendbaren Code zu finden. Sonst überspringen.

## 4. User Perspective ausarbeiten

Fülle die Section mit:

- Wer (welche Persona — meistens Martin, manchmal „externe Person, die einen Atom-Link teilt").
- Was passiert aus deren Sicht (User-Story-artig).
- UI-Skizze als ASCII-Wireframe oder kurze Bildbeschreibung, falls UI-relevant.
- Akzeptanzkriterien als Checkliste mit `- [ ]`.

## 5. Technical Details ausarbeiten

Fülle die Section mit:

- Datenmodell-Änderungen (neue Tabellen, Felder, Migrations-Plan).
- API-Routen-Änderungen.
- Frontend-Komponenten-Änderungen.
- Abhängigkeiten / Dritt-Libraries.
- Test-Strategie (welche Tests neu, was wird gemockt).
- **Out-of-Scope** explizit benennen — was bewusst nicht in diese Spec gehört.

## 6. Open Questions schärfen

Prüfe die existierende Liste. Streiche Fragen, die durch die Ausarbeitung beantwortet sind. Ergänze neue, die durch die Exploration aufgekommen sind.

## 7. Frontmatter pflegen

- `status: planned`.
- `updated:` auf heute setzen.
- Sonst keine Änderungen am Frontmatter (insbes. `name`, `created`, `owner` nicht anfassen).

## 8. Branch + PR

- Erzeuge Branch `spec/<name>-plan` aus aktuellem `main`.
- Committe nur `specs/<name>.md` mit Message `Plan spec: <name>`.
- Push und `gh pr create` mit Titel `Plan: <title>` und Body mit Liste der Open Questions, damit Martin sie in PR-Comments diskutieren kann.

## 9. Bericht an User

Liste die offenen Fragen explizit am Ende deines Turns auf — auch wenn sie schon im PR stehen. Empfehle: „Wenn alle Open Questions geklärt sind, weiter mit `/roast-spec <name>`."
