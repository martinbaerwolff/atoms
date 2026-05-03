# Specs

Spec-Driven Development für Atoms. Jedes Feature, jeder Bug und jede initiale Phase bekommt **genau eine Markdown-Datei** in diesem Ordner, die von der ersten Idee bis zur fertigen Implementierung mitwandert.

## Lifecycle

```
ideated  →  planned  →  roasted  →  in_implementation  →  implemented
                                          │
                                          └→  abandoned (jederzeit)
```

| Status | Skill, der ihn setzt | Bedeutung |
|---|---|---|
| `ideated` | [`/ideate-spec`](../.claude/commands/ideate-spec.md) | Datei existiert, Management Summary gefüllt. |
| `planned` | [`/plan-spec`](../.claude/commands/plan-spec.md) | User Perspective + Technical Details ausformuliert. |
| `roasted` | [`/roast-spec`](../.claude/commands/roast-spec.md) | Spec wurde kritisch hinterfragt, Roast Notes befüllt. |
| `in_implementation` | [`/implement-spec`](../.claude/commands/implement-spec.md) | Branch + erster Commit existieren. |
| `implemented` | [`/implement-spec`](../.claude/commands/implement-spec.md) | PR gemerged, Final Implementation + Implementation Log gefüllt. |
| `abandoned` | manuell | Idee verworfen, Spec bleibt als Lerntext erhalten. |

## Datei-Konvention

- Pfad: `specs/<kebab-case-name>.md` — flach, keine Untergliederung nach Typ.
- Typ steckt im Frontmatter (`type: feature | bug | phase`).
- Datum lebt im Frontmatter, nicht im Dateinamen.
- Template: [`_template.md`](_template.md).

## Modell-Regeln

- Ideate / Plan / Roast → **Opus** (kreatives, kritisches Denken).
- Implement → **Sonnet** (schnelle, präzise Code-Arbeit).

Skills warnen, wenn das falsche Modell aktiv ist, und stoppen vor jeder anderen Aktion.

## Wann *keine* Spec nötig ist

Triviale Bug-Fixes (≤ 10 Zeilen, klare Ursache) brauchen keine Spec. Faustregel: **Wenn der Fix einen eigenen PR rechtfertigt, rechtfertigt er auch eine Mini-Spec** (nur Summary + technische Notiz reichen).
