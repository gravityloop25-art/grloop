# Gravity Loop Dashboard

Lokales Dashboard (Dark-Mode, handytauglich) für den Shorts-Kanal **Gravity Loop**: Übersicht, alle Videos, Upload-Zeitplan, Best-Time-Auswertung. TikTok ist als Platzhalter vorbereitet.

**Stack:** Node.js + Express, SQLite (`better-sqlite3`), schlichtes HTML/JS, Chart.js. Kein Build-Schritt.

## Start

```bash
cd dashboard
npm install
cp .env.example .env     # dann .env ausfüllen (siehe unten)
npm start                # -> http://localhost:3000
```

Nur ansehen, ohne Zugangsdaten (Beispieldaten):

```bash
npm run demo             # -> http://localhost:3000, Banner "DEMO-Modus"
```

Daten werden alle 15 Minuten automatisch geholt (`SYNC_MINUTES`), plus Button „Jetzt aktualisieren“. Alles landet in `data/dashboard.sqlite`.

## .env

| Variable | Bedeutung |
|---|---|
| `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` | aus der Google Cloud Console (unten) |
| `GOOGLE_REDIRECT_URI` | `http://localhost:3000/auth/callback` (muss exakt in der Console stehen) |
| `ALLOWED_EMAIL` | `gravity.loop25@gmail.com` – jedes andere Konto wird abgewiesen |
| `SESSION_SECRET` | beliebiger langer Zufallstext |
| `METRICOOL_TOKEN`, `METRICOOL_BLOG_ID` (8100417), `METRICOOL_USER_ID` | Metricool: Einstellungen → API |

Es werden keine Passwörter abgefragt oder gespeichert. Gespeichert wird nur das Google-Refresh-Token (lokal in SQLite, `data/` ist per `.gitignore` ausgeschlossen). Die App hat nur Lesezugriff (`youtube.readonly`, `yt-analytics.readonly`).

## Google Cloud Console einrichten (Schritt für Schritt)

1. Öffne <https://console.cloud.google.com> und melde dich mit **gravity.loop25@gmail.com** an.
2. Oben auf die Projektauswahl → **Neues Projekt** → Name „Gravity Loop Dashboard“ → **Erstellen**.
3. **APIs & Dienste → Bibliothek**: „**YouTube Data API v3**“ suchen → **Aktivieren**. Dann „**YouTube Analytics API**“ suchen → **Aktivieren**.
4. **APIs & Dienste → OAuth-Zustimmungsbildschirm** (bzw. „Google Auth Platform“):
   - Nutzertyp **Extern**, App-Name „Gravity Loop Dashboard“, Support- und Kontakt-E-Mail: gravity.loop25@gmail.com.
   - Bereiche (Scopes): `.../auth/youtube.readonly` und `.../auth/yt-analytics.readonly` hinzufügen.
   - **Testnutzer**: gravity.loop25@gmail.com eintragen.
   - Status „Wird getestet“ reicht. Hinweis: Im Testmodus läuft das Refresh-Token nach 7 Tagen ab, dann einfach neu anmelden. Wer das nicht will, setzt die App auf „In Produktion“ (für den Eigengebrauch ohne Prüfung möglich, Google zeigt dann eine „nicht verifiziert“-Warnung, die du mit „Erweitert → Weiter“ bestätigst).
5. **Anmeldedaten → Anmeldedaten erstellen → OAuth-Client-ID**:
   - Anwendungstyp **Webanwendung**.
   - Autorisierte Weiterleitungs-URI: `http://localhost:3000/auth/callback`.
   - **Erstellen** → Client-ID und Client-Secret in die `.env` kopieren.
6. `npm start`, <http://localhost:3000> öffnen → „Mit Google anmelden“ → Konto gravity.loop25@gmail.com wählen → Zugriff erlauben (bei mehreren Kanälen den Kanal „Gravity Loop“ wählen).

## Metricool

Token und User-ID findest du in Metricool unter Einstellungen → API. Die geplanten Posts werden für die nächsten 60 Tage geladen (Zeitzone Europe/Berlin).

## Aufbau

- `server.js` Express, Login-Routen, JSON-API
- `google.js` OAuth, Konto-Prüfung, Token-Refresh
- `sync.js` Abruf YouTube Data/Analytics + Metricool → SQLite
- `metricool.js` Metricool-Client · `errors.js` verständliche Fehlermeldungen
- `public/` Oberfläche · `demo.js` Beispieldaten

TikTok später ergänzen: in `server.js` die Route `/api/tiktok` füllen und in `public/app.js` `tiktokView()` ausbauen.

## Grenzen

- Der Views-Verlauf „erste 24 h / 48 h“ kommt pro **Kalendertag** (Tag 1/2/3); stündliche Daten gibt die YouTube-API nicht her.
- „Shorts-Views 90 Tage“ summiert die Views der Shorts (≤ 3 Min) aus Analytics; YouTubes offizielle Zählung fürs Partnerprogramm kann abweichen.
- Best-Time-Empfehlung nutzt die Gesamt-Views je Video nach Veröffentlichungszeit (ältere Videos sind im Vorteil).

## Hosting (von überall erreichbar)

Die App läuft als Docker-Container (`Dockerfile`). Wichtig sind zwei Dinge: eine **feste https-Adresse** und ein **dauerhafter Speicher (Volume) unter `/data`** für die SQLite-Datei und den Login.

Beispiel Railway (andere Hoster wie Render/Fly.io funktionieren genauso):

1. Auf railway.com mit GitHub anmelden → **New Project → Deploy from GitHub repo** → Repo `grloop` wählen, als **Root Directory** `dashboard` setzen.
2. **Volume** hinzufügen, Mount Path `/data`.
3. **Variables** setzen (Werte nur dort eintragen, nie ins Repo):
   - `SESSION_SECRET` (langer Zufallstext), `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
   - `GOOGLE_REDIRECT_URI` = `https://DEINE-ADRESSE/auth/callback`
   - `ALLOWED_EMAIL` = `gravity.loop25@gmail.com`
   - `METRICOOL_TOKEN`, `METRICOOL_BLOG_ID`, `METRICOOL_USER_ID`
4. **Settings → Networking → Generate Domain**: das ist deine Adresse.
5. In der Google Cloud Console beim OAuth-Client die Weiterleitungs-URI `https://DEINE-ADRESSE/auth/callback` **zusätzlich** eintragen.
6. Zustimmungsbildschirm auf **„In Produktion“** stellen, sonst läuft der Login nach 7 Tagen ab.
7. Adresse am Handy/PC öffnen → „Mit Google anmelden“. Am Handy: Browser-Menü → **Zum Startbildschirm hinzufügen** (läuft dann wie eine App).

Sicherheit: Zugriff hat nur, wer sich mit `ALLOWED_EMAIL` bei Google anmeldet. Das Google-Token (nur Lesezugriff) liegt auf dem Volume des Hosters, schütze deshalb dein Hoster-Konto mit 2FA. Der Healthcheck-Pfad ist `/healthz`.
