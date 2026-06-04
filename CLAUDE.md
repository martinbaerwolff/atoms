# CLAUDE.md — Projektregeln

## Wie wir zusammenarbeiten
- Ich bin kein Berufs-Softwareentwickler und lese den Code nicht selbst.
  Ich verantworte Absicht, Spezifikation und Verhalten.
  Du und die automatischen Tore (Tests, Typen, Linter, CI, Review) verantworten den Code.
- Ich entscheide nur über Inhalt und Absicht, NICHT über Technik.
  Triff alle technischen Entscheidungen (Stack, Datenbank, Struktur, Tooling, Hosting)
  selbst, basierend auf dem, was das Projekt wirklich braucht.
  Wähle die einfachste Option, die ausreicht (z. B. SQLite statt PostgreSQL, wenn das genügt).
  Erkläre mir jede wichtige Entscheidung in einfachem Deutsch mit Analogie, bevor du sie
  umsetzt. Ich gebe frei oder frage nach.
- Sprich durchgehend Deutsch, auch in Ausgaben und UI-Texten.
- Bei Unklarheit: nachfragen statt annehmen.
- Mach Verhalten überprüfbar (Akzeptanzkriterien, sichtbare Resultate).

## Aufwand an den Einsatz anpassen
Ordne die Aufgabe ein, bevor du loslegst (frag mich im Zweifel):
- Einmal-Skript: Git + lesbar + prüfen dass es läuft.
- Tool/Bibliothek/Skriptsammlung: + Tests, Lint, Typprüfung, README, CI.
- Prototyp: Tempo vor Politur, klar als Wegwerf kennzeichnen.
- Produktiv-App: volle Tore + Sicherheit + Datenschutz/DSGVO + Backups + Monitoring.

## Immer gültige Regeln
- Plan zuerst: bei allem Nicht-Trivialen zeigen was du tun willst, auf Freigabe warten.
- Git ab der ersten Datei, Remote auf GitHub, kleine Commits, Conventional Commits.
- Keine Secrets in Code oder Git (.env in .gitignore).
- Keine destruktiven Aktionen ohne ausdrückliche Freigabe.
- Evidenz statt Behauptung: nichts als fertig melden ohne Nachweis (Tests grün / App läuft).
- Zustand in Dateien auslagern (Plan, Entscheidungen), damit nichts zwischen Sitzungen verloren geht.

## Superpowers
- Superpowers ist das Standard-Vorgehen für Planung, TDD, Subagenten und Review.
- Diese Datei steht darüber: wo etwas kollidiert, gilt diese Datei.

## Modell-Konfiguration
- Immer `opusplan` als Modell-Einstellung: Opus für Planung (Plan-Modus), Sonnet für Implementierung.
- Pläne, Designs und Brainstorming immer in einer Planungs-Session mit Opus schreiben.
- Wenn das Modell nicht `opusplan` ist, den Nutzer darauf hinweisen und `/model opusplan` vorschlagen.

## Session-Workflow (wichtig)
Planung und Implementierung laufen in getrennten Sessions:

1. **Planungs-Session (Opus):** Brainstorming → Design-Dokument → Implementierungsplan.
   Alles wird als Dateien gespeichert unter `docs/superpowers/`.
2. **Implementierungs-Session (Sonnet):** Neue Claude Code Session öffnen → `/executing-plans` eingeben.
   Sonnet bekommt nur den Plan, keinen langen Chat-Verlauf.
3. **Zwischen Phasen:** Jede Phase startet in einer eigenen frischen Session.

**Beim Start einer neuen Session:**
- Prüfe ob ein offener Implementierungsplan existiert (`docs/superpowers/plans/`).
  Falls ja: biete dem Nutzer an, `/executing-plans` zu starten — aber frag erst, mach es nicht automatisch.
- Prüfe offene GitHub Issues (`gh issue list --state open`) und offene Pull Requests (`gh pr list --state open`).
  Fasse kurz zusammen was offen ist, damit der Nutzer entscheiden kann womit wir anfangen.

**In laufenden Sessions:** Warne den Nutzer, wenn er Implementierungsarbeit in einer
Planungs-Session macht oder der Kontext zu lang wird — und schlage vor, in eine neue
Session zu wechseln.
