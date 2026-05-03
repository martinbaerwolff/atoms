---
description: Implementiert eine Spec, loggt Entscheidungen und Abweichungen, setzt Status auf `in_implementation` → `implemented`
---

# /implement-spec

Du sollst eine Spec im Status `roasted` (oder `planned` mit Warnung) tatsächlich umsetzen — Branch, Code, Tests, PR, Spec-Updates.

## 1. Modell-Gate (BLOCKING)

Lies die „You are powered by"-Zeile. Wenn sie **nicht** `Sonnet` enthält:

> **STOP.** Antworte ausschließlich mit:
>
> „Dieser Skill braucht **Sonnet** für effiziente Implementierung (gerade läuft `<aktuelles-modell>`). Bitte mit `/model claude-sonnet-4-6` wechseln und `/implement-spec <name>` neu aufrufen."
>
> Beende den Turn.

## 2. Spec laden + validieren

- Argument hinter `/implement-spec` ist der Spec-Name. Wenn leer: per AskUserQuestion fragen oder die zuletzt geänderte Spec im Status `roasted` vorschlagen.
- Lies `specs/<name>.md`.
- Prüfe `status`:
  - `roasted` → ok, normaler Lauf.
  - `planned` → Warnung: „Spec ist noch nicht roasted. Trotzdem implementieren?" per AskUserQuestion. Bei „Nein" → STOP mit Hinweis auf `/roast-spec`.
  - `ideated` → STOP. Erst `/plan-spec`, dann `/roast-spec`.
  - `in_implementation` → ok, Re-Entry nach Unterbrechung.
  - `implemented` → STOP („bereits implementiert; für Änderungen neue Spec anlegen").
  - `abandoned` → STOP („Spec ist abgebrochen").

## 3. Branch + Status-Update

- Erzeuge Branch aus aktuellem `main`. Branch-Name: an Spec-Name angelehnt, z.B. `feat/<name>` oder `fix/<name>` (je `type`).
- Setze `status: in_implementation` und `updated:` heute in der Spec.
- Committe diese Frontmatter-Änderung allein, Message: `Start implementation: <name>`.

## 4. Implementierung nach TDD

Folge `skills/tdd.md`:

1. Failing Test schreiben → rot bestätigen.
2. Minimale Implementierung → grün.
3. Refactor wenn nötig.
4. Kleinen Commit machen.

Loop fortführen bis Akzeptanzkriterien erfüllt.

## 5. Implementation Log pflegen

**Pflicht:** schreibe einen Log-Eintrag in `## Implementation Log` der Spec, wenn:

- Du eine Bibliothek/Pattern wählst, das nicht in den Technical Details stand.
- Du von Spec-Vorgaben abweichst.
- Du auf einen unerwarteten Bug oder eine technische Hürde stößt, die das Vorgehen ändert.
- Eine Akzeptanzkriterium nicht so umgesetzt werden kann, wie geplant.

Format:
```
- YYYY-MM-DD — <Entscheidung/Abweichung>: <was und warum>
```

Neueste Einträge oben.

## 6. `make check` grün halten

Nach jeder Test+Code-Iteration: `make check` lokal grün halten. Vor dem PR: einmal vollständig laufen lassen.

## 7. PR erstellen (vor Merge)

- Push den Branch.
- `gh pr create` mit:
  - Titel: kurzer Imperativ, max 70 Zeichen.
  - Body: zitiert die Management Summary der Spec, verlinkt `specs/<name>.md`, listet die abgehakten Akzeptanzkriterien als Checkliste.
- Spec-Updates (Implementation Log, Status, etc.) sind im selben PR — **nicht** separat.

## 8. Nach Merge: Final Implementation

Nach dem Merge zurück auf `main`, lokal `git pull`. Dann eine letzte Spec-Aktualisierung als kleinen Follow-up-Commit auf einem `spec/<name>-finalize`-Branch (separater PR), oder — falls noch im selben PR möglich — direkt:

- Fülle `## Final Implementation`: 5–10 Bullet-Punkte was *tatsächlich* gebaut wurde.
- Trage PR-Nummer in Frontmatter `related_prs` ein.
- Setze `status: implemented`, `updated:` heute.

## 9. Bericht an User

- PR-URL.
- Anzahl Commits, Tests, Zeilen geändert.
- Empfehle nächste Schritte (z.B. neue Spec für dependent feature).
