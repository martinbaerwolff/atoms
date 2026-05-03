---
description: Erstellt eine neue Spec im Status `ideated` aus einer Freitext-Beschreibung
---

# /ideate-spec

Du sollst aus einer Freitext-Beschreibung der User-Idee eine neue Spec-Datei in `specs/` anlegen, mit `status: ideated`, sinnvollem kebab-case-Namen und gefüllter Management Summary.

## 1. Modell-Gate (BLOCKING — vor allem anderen)

Lies die „You are powered by"-Zeile aus dem System-Prompt. Wenn sie **nicht** `Opus` enthält:

> **STOP.** Antworte ausschließlich mit:
>
> „Dieser Skill braucht **Opus** für ideatives Denken (gerade läuft `<aktuelles-modell>`). Bitte mit `/model claude-opus-4-7` wechseln und `/ideate-spec` neu aufrufen."
>
> Mache keinen weiteren Tool-Call. Beende den Turn.

## 2. Eingabe parsen

Die Beschreibung kommt als Argument hinter `/ideate-spec`. Wenn leer: frage per AskUserQuestion „Worum geht's? Beschreib die Idee in 1–3 Sätzen." und warte.

## 3. Existing-Specs-Check

Lies `specs/`-Inhalt. Bestimme alle bestehenden `name:`-Werte (Frontmatter) und Dateinamen. Vermeide bei der Namensvergabe Substring-Kollisionen mit existierenden Namen.

## 4. Namens-Vorschläge

Schlage **2–3 sinnvolle kebab-case-Namen** vor, die:

- aus der Beschreibung herleitbar sind (kein generisches `feature-x`),
- 2–5 Worte lang sind,
- weder bestehende Specs überlappen noch reservierte Präfixe nutzen (`phase-` ist Phasen vorbehalten).

Frage per AskUserQuestion welcher Name verwendet werden soll. Lass „Other" zu, damit der User auch eigenen Namen tippen kann.

## 5. Typ bestimmen

`type` ist meistens aus dem Kontext klar:

- Steht „Bug", „Fehler", „regression" o.ä. drin → `bug`.
- Beginnt der Name mit `phase-` → `phase`.
- Sonst → `feature`.

Bei Unsicherheit: per AskUserQuestion fragen.

## 6. Spec-Datei schreiben

Erzeuge `specs/<gewählter-name>.md` mit:

- Frontmatter: alle Felder aus dem Template, `status: ideated`, `created` und `updated` = heute.
- `## Management Summary` voll ausformuliert (1–3 Sätze, basierend auf der User-Beschreibung).
- `## User Perspective` und `## Technical Details` nur als 1–2 Stichpunkt-Skizzen, falls aus der Beschreibung schon ableitbar — sonst leer mit Kommentar `_(wird in /plan-spec befüllt)_`.
- `## Open Questions` mit allem, was beim Lesen der Beschreibung sofort offen ist.
- Restliche Sections leer mit den Standard-Kommentar-Hinweisen aus `_template.md`.

## 7. Branch + PR

- Erzeuge Branch `spec/<name>-ideate` aus aktuellem `main`.
- Committe nur `specs/<name>.md` mit Message `Ideate spec: <name>`.
- Push und `gh pr create` mit Titel `Ideate: <title>` und Body, der die Management Summary zitiert + erwähnt, dass dies der erste Schritt im Spec-Lifecycle ist.

## 8. Bericht an User

Gib am Ende eine Zwei-Zeilen-Zusammenfassung: „Spec `<name>` angelegt im Status `ideated`. PR: <url>. Nächster Schritt: `/plan-spec <name>`."
