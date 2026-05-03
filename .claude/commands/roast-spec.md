---
description: Hinterfragt eine Spec kritisch, befüllt Roast Notes, setzt Status auf `roasted`
---

# /roast-spec

Du sollst eine Spec im Status `planned` (oder `roasted`, für erneuten Roast) kritisch hinterfragen, mindestens fünf substantielle Schwachstellen / Lücken / Risiken finden und sie inklusive vorgeschlagener Auflösung in „Roast Notes" festhalten.

## 1. Modell-Gate (BLOCKING)

Lies die „You are powered by"-Zeile. Wenn sie **nicht** `Opus` enthält:

> **STOP.** Antworte ausschließlich mit:
>
> „Dieser Skill braucht **Opus** für gründliche Kritik (gerade läuft `<aktuelles-modell>`). Bitte mit `/model claude-opus-4-7` wechseln und `/roast-spec <name>` neu aufrufen."
>
> Beende den Turn.

## 2. Spec laden + validieren

- Argument hinter `/roast-spec` ist der Spec-Name. Wenn leer: per AskUserQuestion fragen.
- Lies `specs/<name>.md`.
- Prüfe `status`:
  - `planned` → ok, normaler Lauf.
  - `roasted` → idempotenter Re-Roast. Hänge neuen Roast-Block an statt zu überschreiben.
  - alles andere → STOP mit Erklärung („Spec ist `<status>` — Roast vor Plan oder nach Implementation macht keinen Sinn").

## 3. Codebase querlesen

Wenn die Spec konkrete technische Entscheidungen nennt (Libraries, Architektur-Muster, Datenstrukturen): lies relevante Stellen im Code, um beurteilen zu können, ob die Spec-Annahmen zur Realität passen. 1 Explore-Subagent reicht meistens.

## 4. Roast schreiben

Finde **mindestens 5 Punkte**. Suche aktiv in folgenden Dimensionen:

- **Edge Cases:** Was bricht bei null/leer/sehr groß/parallel/offline?
- **Akzeptanzkriterien:** Sind sie testbar? Vollständig? Messbar?
- **Tech-Debt-Risiken:** Workarounds, Hard-Codings, fehlende Abstraktionen.
- **Scope-Creep:** Schleicht sich was rein, das in eine eigene Spec gehört?
- **Out-of-Scope-Lücken:** Wurde das Wichtigste explizit ausgeschlossen oder nur weggelassen?
- **Missing Tests:** Welche Tests fehlen, die *nicht* offensichtlich sind?
- **Konsistenz mit existierenden Specs / CLAUDE.md / Konventionen.**
- **User-Experience-Gaps:** Was fühlt sich umständlich an?

Falls du wirklich keine 5 Punkte findest, hänge mind. 2 substantielle Punkte an und schreibe explizit „Keine größeren Mängel gefunden — geprüft wurden: …".

Format eines Roast-Blocks:

```markdown
### Roast 2026-05-04 (claude-opus-4-7)

**R1: <kurzer Titel>**

- _Risiko:_ …
- _Auflösung:_ … (wer hat zu tun: User entscheiden / Spec aktualisieren / akzeptieren).

**R2: …**
…
```

Bei Re-Roast (Status war schon `roasted`): hänge unter dem alten Block einen neuen mit anderem Datum an. Nichts überschreiben.

## 5. Spec-Body anpassen

Wo der Roast offensichtlich neue Akzeptanzkriterien, Out-of-Scope-Punkte oder geänderte Technical Details nahelegt: **mache die Änderungen direkt in der Spec**, mit knapper Begründung im jeweiligen Roast-Punkt („→ siehe geänderten Punkt 3 in Technical Details").

## 6. Frontmatter pflegen

- `status: roasted`.
- `updated:` auf heute setzen.

## 7. Branch + PR

- Erzeuge Branch `spec/<name>-roast` aus aktuellem `main`.
- Committe nur `specs/<name>.md` mit Message `Roast spec: <name>`.
- Push und `gh pr create` mit Titel `Roast: <title>` und Body, der die wichtigsten 2–3 Roast-Punkte zitiert.

## 8. Bericht an User

Liste alle Roast-Punkte in einem Satz pro Punkt am Ende deines Turns. Empfehle: „Wenn die Auflösungen passen, mit `/implement-spec <name>` weitermachen."
