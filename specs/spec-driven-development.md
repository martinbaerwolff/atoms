---
name: spec-driven-development
title: Spec-Driven Development für Atoms
type: feature
status: implemented
created: 2026-05-03
updated: 2026-05-03
owner: martin
related_prs: []
---

# Spec-Driven Development für Atoms

## Management Summary

Jede neue Idee in Atoms — Feature, Bug, oder Phase der initialen Implementierung — bekommt eine eingecheckte Markdown-Spec, die von der ersten Idee bis zum gemergten Code mitwandert. Vier Slash-Commands (`/ideate-spec`, `/plan-spec`, `/roast-spec`, `/implement-spec`) führen die Spec durch ihren Lebenszyklus. Quelle der Wahrheit für *was wird gebaut und warum* ist die Spec, nicht der Commit-Message-Body oder die PR-Description.

## User Perspective

**Martin** (alleiniger Nutzer und Entwickler) will:

- jede Idee sofort als Spec festhalten, auch wenn sie noch unscharf ist;
- später ohne Code-Archäologie nachvollziehen, *warum* eine Entscheidung gefallen ist;
- Implementierungen, die vom ursprünglichen Plan abweichen, sehen können — inklusive Begründung;
- den Workflow soweit automatisieren, dass er nicht selbst Frontmatter pflegen oder Branches anlegen muss.

Workflow aus Sicht des Users:

```
Idee → /ideate-spec "Beschreibung"  → specs/<name>.md (status: ideated)
                                    → eigener PR mit nur dieser Datei
     → /plan-spec <name>            → User/Tech Details gefüllt (status: planned)
                                    → Update-PR
     → /roast-spec <name>           → Roast Notes (status: roasted)
                                    → Update-PR
     → /implement-spec <name>       → Branch + Code + Spec-Updates (status: in_implementation)
                                    → PR mit Code + Spec-Updates
     → Merge                        → status: implemented
```

Akzeptanzkriterien:

- [x] `specs/`-Ordner existiert mit README, Template und Backfill-Specs für Phase 0/1/2.
- [x] Vier Slash-Commands existieren in `.claude/commands/` und enthalten konkrete Schritte.
- [x] Modell-Gate stoppt jede Skill-Ausführung mit klarer Anweisung zum manuellen `/model`-Switch, wenn falsche Modell-Familie aktiv ist.
- [x] CLAUDE.md kennt das Spec-System und verweist auf `specs/README.md`.

## Technical Details

**Verzeichnisstruktur:**

```
specs/
├── README.md                          # Lebenszyklus-Erklärung
├── _template.md                       # leeres Template
├── spec-driven-development.md         # diese Datei (Meta + Dogfooding)
├── phase-0-tooling-skeleton.md        # Backfill
├── phase-1-db-schema-and-crud.md      # Backfill
├── phase-2-atoms-feed-ui.md           # Backfill
└── phase-3-metadata-pickers.md        # status: ideated
.claude/commands/
├── ideate-spec.md
├── plan-spec.md
├── roast-spec.md
└── implement-spec.md
```

**Frontmatter-Schema:**

| Feld | Typ | Pflicht | Beschreibung |
|---|---|---|---|
| `name` | string | ja | kebab-case, identisch mit Dateinamen ohne `.md` |
| `title` | string | ja | menschenlesbarer Titel, darf Sonderzeichen enthalten |
| `type` | enum | ja | `feature` \| `bug` \| `phase` |
| `status` | enum | ja | siehe Lifecycle-Tabelle in `specs/README.md` |
| `created` | date | ja | ISO YYYY-MM-DD |
| `updated` | date | ja | ISO YYYY-MM-DD, von Skills automatisch gepflegt |
| `owner` | string | ja | für Atoms immer `martin` |
| `related_prs` | string[] | ja | PR-Referenzen wie `"#42"`, leer bis Implementierung |

**Modell-Gate:**

- Skill liest „You are powered by"-Zeile aus dem System-Prompt.
- Substring-Match (`opus`/`sonnet`) — Versionen werden nicht unterschieden.
- Bei Mismatch: STOP, Nachricht im Format „Skill braucht **Opus** (gerade läuft `claude-sonnet-4-6`). Bitte mit `/model claude-opus-4-7` wechseln und `/<skill>` neu aufrufen." — kein Override-Pfad, da User den Skill nach `/model`-Switch jederzeit wieder aufrufen kann.

**Git-Workflow:**

- Spec-only-Skills (`ideate`/`plan`/`roast`) erzeugen automatisch Branch + PR. Branch-Name: `spec/<kebab-name>-<phase>`.
- `/implement-spec` legt Feature-Branch an. Spec-Updates (Implementation Log, Final Implementation, related_prs, status) landen im *selben* PR wie der Code.

**Out-of-Scope (für diese Spec):**

- Spec-Validator-Tooling (z.B. CI-Check für Frontmatter-Schema).
- Auto-Linking zwischen Specs (z.B. „blockt durch X").
- Spec-Suche / Index-Generierung.

## Open Questions

Keine offenen Fragen — alle Open Questions wurden im Plan vor der Umsetzung beantwortet (Backfill-Umfang, Git-Flow, Dogfooding).

## Roast Notes

Roast fand vor Implementierung im Plan-File statt — siehe `~/.claude/plans/starte-phase-2-cryptic-wigderson.md` (R1–R12). Auflösungen sind in den Plan eingearbeitet und in dieser Spec reflektiert. Wichtigste Punkte:

- **Modell-Gate als Hard-Stop** statt Override-Frage, weil claude-code-guide bestätigt hat: programmatischer `/model`-Switch existiert nicht.
- **Status `roasted`** beibehalten (statt `reviewed`), weil präziser für Selbst-Kritik durch Claude.
- **Phase 0/1/2 backfillen** trotz initialer Skepsis — User entschieden, weil Format-Beispiele sonst rar wären.
- **Trivial-Bug-Ausnahme** (≤10 LoC, klare Ursache) explizit dokumentiert, sonst wird das System für Mikro-Fixes zur Bremse.

## Implementation Log

- 2026-05-03 — Plan + Roast in Plan-File geschrieben, drei offene Fragen per AskUserQuestion geklärt.
- 2026-05-03 — claude-code-guide kontaktiert: programmatischer Modell-Switch existiert nicht → Hard-Stop-Gate.
- 2026-05-03 — `specs/`-Struktur, Skills und CLAUDE.md-Anpassung in einem Branch zusammen umgesetzt (Bootstrap, daher kein eigener PR pro Skill-Anlage).
- 2026-05-03 — Branch-Naming-Konvention für Skills festgelegt: `spec/<kebab-name>-<phase>` für ideate/plan/roast, `feat/<kebab-name>` o.ä. für implement (folgt sonstigem Repo-Stil).

## Final Implementation

- `specs/`-Ordner mit README, Template, Meta-Spec und Backfill-Specs für Phase 0–3.
- 4 Slash-Commands unter `.claude/commands/` mit identischem Modell-Gate-Verhalten.
- CLAUDE.md erweitert um Abschnitt „Spec-driven development" und Hard Rule #9.
- PRs: _wird beim Merge ergänzt._
