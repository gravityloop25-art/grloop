# Arbeitsregeln für dieses Repo

## Graphify zuerst (immer)

Dieses Repo hat einen Wissensgraphen in `graphify-out/` (`GRAPH_REPORT.md`, `graph.json`, `graph.html`, Obsidian-Vault in `graphify-out/obsidian/`).

- **Zu Beginn jeder Sitzung:** zuerst `graphify-out/GRAPH_REPORT.md` lesen, nicht den ganzen Code durchsuchen.
- **Fragen zum Code** erst mit `graphify query "<Frage>"`, `graphify explain "<Name>"` oder `graphify path "A" "B"` beantworten. Nur die dort genannten Dateien gezielt öffnen.
- **Nach Codeänderungen:** `graphify update .` (lokal, ohne API-Kosten) und danach `graphify export obsidian`, dann `graphify-out/` mitcommitten.
- Ohne API-Key immer `--code-only` verwenden (Docs werden dann nicht ausgewertet).
- Installation falls nötig: `pip install graphifyy` (zwei „y“, das ist der offizielle PyPI-Name).

## Projekt

- `code/` Python-Skripte für die Shorts-Videos, `videos/` fertige Videos.
- `dashboard/` Web-Dashboard (Node/Express, SQLite, Chart.js). Start: siehe `dashboard/README.md`.
- `apps/` Desktop-App (Electron) und Android-App (Capacitor), gebaut per `.github/workflows/build-apps.yml`; Details in `apps/README.md`.
- Konto nur gravity.loop25@gmail.com. Keine Passwörter oder Secrets speichern oder committen (`.env` bleibt lokal).
