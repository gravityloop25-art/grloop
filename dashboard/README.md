# Gravity Loop Dashboard

Lokales Dashboard (Dark-Mode, handytauglich) für den Shorts-Kanal **Gravity Loop**: Übersicht, alle Videos, Upload-Zeitplan, Best-Time-Auswertung. TikTok ist als Platzhalter vorbereitet.

**Stack:** Node.js + Express, SQLite/Turso (`@libsql/client`), schlichtes HTML/JS, Chart.js. Kein Build-Schritt.

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

Daten werden beim Öffnen geholt, wenn sie älter als 15 Minuten sind (`SYNC_MINUTES`), plus Button „Jetzt aktualisieren“. Lokal landet alles in `data/dashboard.sqlite`, auf Vercel in Turso.

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
- `sync.js` Abruf YouTube Data/Analytics + Metricool → Datenbank (in Teilschritten)
- `session.js` signierte Login-Cookies · `api/index.js` + `vercel.json` Vercel-Einstieg
- `metricool.js` Metricool-Client · `errors.js` verständliche Fehlermeldungen
- `public/` Oberfläche · `demo.js` Beispieldaten

TikTok später ergänzen: in `server.js` die Route `/api/tiktok` füllen und in `public/app.js` `tiktokView()` ausbauen.

## Grenzen

- Der Views-Verlauf „erste 24 h / 48 h“ kommt pro **Kalendertag** (Tag 1/2/3); stündliche Daten gibt die YouTube-API nicht her.
- „Shorts-Views 90 Tage“ summiert die Views der Shorts (≤ 3 Min) aus Analytics; YouTubes offizielle Zählung fürs Partnerprogramm kann abweichen.
- Best-Time-Empfehlung nutzt die Gesamt-Views je Video nach Veröffentlichungszeit (ältere Videos sind im Vorteil).

## Hosting auf Vercel (empfohlen, von überall erreichbar)

Die App läuft auf Vercel (Serverless), die Daten liegen in **Turso** (SQLite in der Cloud, Gratis-Tarif). Aktualisiert wird **beim Öffnen** der App (und wenn du zu ihr zurückkehrst), sobald die Daten älter als 15 Minuten sind, in fünf kurzen Schritten (Kanal, Videos, Analytics, 90 Tage, Zeitplan). Ein Hintergrund-Timer ist auf Vercel nicht nötig.

1. **Turso:** auf turso.tech mit GitHub anmelden → Datenbank anlegen (Region in der EU) → URL (`libsql://…`) kopieren und unter „Create Token“ einen Token erzeugen.
2. **Vercel:** auf vercel.com mit GitHub anmelden → **Add New → Project** → Repo `grloop` importieren → **Root Directory: `dashboard`**, Framework „Other“.
3. **Environment Variables** eintragen (nur dort, nie ins Repo):
   - `TURSO_DATABASE_URL`, `TURSO_AUTH_TOKEN`
   - `SESSION_SECRET` (langer Zufallstext)
   - `ALLOWED_EMAIL` = `gravity.loop25@gmail.com`
   - `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
   - `GOOGLE_REDIRECT_URI` = `https://DEINE-ADRESSE.vercel.app/auth/callback`
   - `METRICOOL_TOKEN`, `METRICOOL_BLOG_ID` (8100417), `METRICOOL_USER_ID`
4. **Deploy.** Danach bei Vercel die Adresse kopieren, `GOOGLE_REDIRECT_URI` damit setzen und **neu deployen** (Variablen wirken erst nach einem neuen Deploy).
5. **Deployment Protection:** In Vercel unter Settings → Deployment Protection für Production **keinen** Vercel-Login verlangen, sonst kommen die Apps nicht durch. Der Schutz ist Google-Login mit `ALLOWED_EMAIL`.
6. In der Google Cloud Console `https://DEINE-ADRESSE.vercel.app/auth/callback` als Weiterleitungs-URI eintragen und den Zustimmungsbildschirm auf „In Produktion“ stellen.
7. Adresse am Handy/PC öffnen → „Mit Google anmelden“. Am Handy: Browser-Menü → **Zum Startbildschirm hinzufügen**.

Sicherheit: Zugriff hat nur, wer sich mit `ALLOWED_EMAIL` anmeldet. Das Google-Token (nur Lesezugriff) liegt in deiner Turso-Datenbank. Schütze Turso-, Vercel- und GitHub-Konto mit 2FA. Der Vercel-Hobby-Tarif ist für private Nutzung gedacht.

Lokal ohne Turso: `npm start` nutzt automatisch eine SQLite-Datei in `data/`.

### Alternative: Docker
Das `Dockerfile` läuft weiterhin bei jedem Hoster mit Volume (`/data`); dann `HOST=0.0.0.0` und `SESSION_SECRET` setzen.
