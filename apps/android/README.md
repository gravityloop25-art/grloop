# Android-App

Hülle (Capacitor) um das gehostete Dashboard. Gebaut wird in GitHub Actions, siehe `../README.md`.
Lokal (Android Studio nötig): `APP_URL=https://… npm run config && npm i @capacitor/core @capacitor/cli @capacitor/android @capacitor/app @capacitor/browser && npx cap add android && python3 scripts/patch-manifest.py && npx cap sync android`.
