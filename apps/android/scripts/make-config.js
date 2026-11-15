// Schreibt capacitor.config.json mit der Server-Adresse aus APP_URL.
const url = (process.env.APP_URL || '').replace(/\/$/, '');
if (!/^https:\/\/[^/]+/.test(url)) { console.error('APP_URL fehlt oder ist nicht https://… (z. B. https://dein-dashboard.up.railway.app)'); process.exit(1); }
require('fs').writeFileSync('capacitor.config.json', JSON.stringify({
  appId: 'com.gravityloop.dashboard', appName: 'Gravity Loop', webDir: 'www',
  server: { url, cleartext: false, allowNavigation: [new URL(url).host] },
  android: { backgroundColor: '#000000' },
}, null, 2));
console.log('capacitor.config.json für', url);
