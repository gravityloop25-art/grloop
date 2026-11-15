// Füllt eine SEPARATE Demo-Datenbank mit Beispieldaten (nur zum Ansehen/Testen der Oberfläche).
process.env.DB_FILE = require('path').join(__dirname, 'data', 'demo.sqlite');
delete process.env.TURSO_DATABASE_URL;
const fs = require('fs'); for (const e of ['', '-wal', '-shm']) { try { fs.unlinkSync(process.env.DB_FILE + e); } catch {} }
const { batch, setKV } = require('./db');
(async () => {
  let seed = 7; const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  const names = ['Ziegelmauer', 'Wachsende Kugel', 'Doppel-Ring', 'Farb-Ausbruch', 'Magnet', 'Gravity-Zahnrad', 'Schläger', 'Plinko', 'Countdown', 'Eis-Zahnrad', 'Feuer-Zahnrad', 'Glühende Kugel'];
  const now = Date.now(); const st = []; let total = 0;
  for (let i = 0; i < 40; i++) {
    const t = new Date(now - (i * 1.5 + 0.3) * 864e5); t.setUTCHours([16, 18, 11, 7][i % 4], 0, 0, 0);
    const views = Math.round(500 + rnd() ** 3 * 90000 * (i % 4 === 1 ? 1.8 : 1)); total += views;
    const thumb = `data:image/svg+xml;utf8,${encodeURIComponent(`<svg xmlns='http://www.w3.org/2000/svg' width='90' height='160'><rect width='90' height='160' fill='hsl(${(i * 47) % 360},70%,25%)'/><circle cx='45' cy='80' r='22' fill='hsl(${(i * 47 + 180) % 360},100%,60%)'/></svg>`)}`;
    st.push(['INSERT INTO videos VALUES(?,?,?,?,?,?,?,?,?,?,?,?)', ['demo' + i, `${names[i % names.length]} #${Math.floor(i / names.length) + 1}`, thumb, t.toISOString(), 30 + (i % 20), views, Math.round(views * 0.06), Math.round(views * 0.002), 18 + rnd() * 12, 60 + rnd() * 40, Math.round(views / 900), Math.round(views * (i < 30 ? 1 : 0.8))]]);
    [0.62, 0.25, 0.08].forEach((f, d) => st.push(['INSERT INTO video_daily VALUES(?,?,?,?)', ['demo' + i, d, new Date(t.getTime() + d * 864e5).toISOString().slice(0, 10), Math.round(views * f * (0.8 + rnd() * 0.4))]]));
  }
  for (let d = 120; d >= 0; d--) st.push(['INSERT INTO daily VALUES(?,?,?,?)', [new Date(now - d * 864e5).toISOString().slice(0, 10), Math.round(800 + rnd() * 3000 + (120 - d) * 60), 100 + rnd() * 900, Math.round(rnd() * 12)]]);
  const pad = (n) => String(n).padStart(2, '0');
  for (let d = 0; d < 14; d++) for (const [h, m, net] of [[18, 0, 'youtube'], [18, 30, 'tiktok'], [11, 0, 'youtube']]) {
    if (rnd() < 0.35) continue;
    const t = new Date(now + d * 864e5);
    st.push(['INSERT INTO posts VALUES(?,?,?,?,?,?)', [`demo-p${d}${h}${net}`, net, 'Geplantes Short ' + (d + 1), `${t.getFullYear()}-${pad(t.getMonth() + 1)}-${pad(t.getDate())}T${pad(h)}:${pad(m)}:00`, 'pending', 'metricool']]);
  }
  await batch(st);
  await setKV('channel', { id: 'UCdemo', title: 'Gravity Loop', subscribers: 640, totalViews: total, videoCount: 40, publishedAt: new Date(now - 90 * 864e5).toISOString() });
  await setKV('sync_meta', { lastSync: new Date().toISOString() });
  console.log('Demo-Datenbank erstellt.');
})();
