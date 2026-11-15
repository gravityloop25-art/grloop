# Apps: Android-APK + Desktop

Beide Apps sind native Hüllen um das **gehostete** Dashboard (siehe `dashboard/README.md`, Abschnitt Hosting). Daten und Google-Login liegen auf dem Server, deshalb sehen Handy und PC dasselbe.

- `desktop/` Electron → Windows (`.exe`), macOS (`.dmg`), Linux (`.AppImage`)
- `android/` Capacitor → `GravityLoop.apk`
- Gebaut wird automatisch in GitHub Actions: `.github/workflows/build-apps.yml`

## Login in den Apps
Google erlaubt keinen Login in eingebetteten Fenstern. Die App öffnet den Login deshalb im System-Browser. Danach kommt sie per `gravityloop://`-Link zurück und löst einen Einmal-Code (2 Minuten gültig, mit PKCE-Prüfung) gegen die Anmeldung ein. Nur gravity.loop25@gmail.com kommt durch.

## Apps bauen
1. Dashboard hosten, Adresse notieren (z. B. `https://xyz.up.railway.app`).
2. GitHub → Repo → **Settings → Secrets and variables → Actions → Variables** → `APP_URL` = deine Adresse. (Oder die Adresse beim Start des Workflows eintragen.)
3. **Actions → „Apps bauen“ → Run workflow.** Der Workflow muss dafür auf dem Standard-Branch (main) liegen: Branch `ccr-dc44a82b-rffbcu` zuerst mergen. Alternativ einen Tag `apps-v1` pushen, das startet den Build auch.
4. Nach ca. 10–15 Minuten: Repo → **Releases** → „Gravity Loop Apps“ → Dateien herunterladen.

## Installieren
- **Android:** `GravityLoop.apk` am Handy öffnen, „Installation aus unbekannten Quellen“ erlauben. Die APK ist Debug-signiert (für den Eigengebrauch ok, nicht für den Play Store).
- **Windows:** `.exe` starten. SmartScreen warnt bei unsignierten Apps: „Weitere Informationen → Trotzdem ausführen“.
- **macOS:** `.dmg` öffnen, App in Programme ziehen, beim ersten Start Rechtsklick → Öffnen (unsigniert).
- **Linux:** `.AppImage` ausführbar machen und starten.
