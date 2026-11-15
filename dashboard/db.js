// Datenbank: Turso (libSQL, SQLite in der Cloud) auf Vercel, lokal eine SQLite-Datei.
const { createClient } = require('@libsql/client');
const path = require('path');
const fs = require('fs');

// Werte aus Umgebungsvariablen säubern (Leerzeichen, Anführungszeichen) und libsql:// auf https:// (HTTP) umstellen,
// das ist auf Serverless-Hostern zuverlässiger als WebSocket.
const clean = (v) => String(v || '').trim().replace(/^["']|["']$/g, '').trim();
let tursoUrl = clean(process.env.TURSO_DATABASE_URL);
if (tursoUrl.startsWith('libsql://')) tursoUrl = 'https://' + tursoUrl.slice('libsql://'.length);
const url = tursoUrl || (() => {
  const f = process.env.DB_FILE || path.join(__dirname, 'data', 'dashboard.sqlite');
  fs.mkdirSync(path.dirname(path.resolve(f)), { recursive: true });
  return 'file:' + path.resolve(f);
})();
const client = createClient({ url, authToken: clean(process.env.TURSO_AUTH_TOKEN) || undefined });

const SCHEMA = `
CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS videos (
  id TEXT PRIMARY KEY, title TEXT, thumb TEXT, published_at TEXT, duration_s INTEGER,
  views INTEGER DEFAULT 0, likes INTEGER DEFAULT 0, comments INTEGER DEFAULT 0,
  avg_view_s REAL, avg_view_pct REAL, subs_gained INTEGER DEFAULT 0, views90 INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS daily (date TEXT PRIMARY KEY, views INTEGER, minutes REAL, subs INTEGER);
CREATE TABLE IF NOT EXISTS posts (id TEXT PRIMARY KEY, network TEXT, text TEXT, start TEXT, status TEXT, source TEXT);
CREATE TABLE IF NOT EXISTS app_codes (code TEXT PRIMARY KEY, challenge TEXT, expires INTEGER);
CREATE TABLE IF NOT EXISTS video_daily (video_id TEXT, day_idx INTEGER, date TEXT, views INTEGER, PRIMARY KEY (video_id, day_idx));
`;
let ready = null;
const init = () => (ready ||= client.executeMultiple(SCHEMA).catch((e) => { ready = null; throw e; }));

// Verständliche Meldung statt rohem Datenbankfehler (und Eintrag ins Vercel-Protokoll).
const guard = async (fn) => {
  try { return await fn(); } catch (e) {
    console.error('[db]', e && e.code, e && e.message);
    const hint = tursoUrl ? ' Prüfe TURSO_DATABASE_URL und TURSO_AUTH_TOKEN in den Vercel-Variablen (Token neu erzeugen, dann Redeploy).' : '';
    throw new Error(`Datenbank-Fehler: ${e && e.message ? e.message : e}.${hint}`);
  }
};
const rowsOf = (rs) => rs.rows.map((r) => Object.fromEntries(rs.columns.map((c, i) => [c, r[i]])));
const q = (sql, args = []) => guard(async () => { await init(); return rowsOf(await client.execute({ sql, args })); });
const run = (sql, args = []) => guard(async () => { await init(); return client.execute({ sql, args }); });
const batch = (stmts) => guard(async () => { await init(); if (stmts.length) await client.batch(stmts.map(([sql, args = []]) => ({ sql, args })), 'write'); });

const getKV = async (k, def = null) => { const r = (await q('SELECT value FROM kv WHERE key=?', [k]))[0]; return r ? JSON.parse(r.value) : def; };
const setKV = (k, v) => run('INSERT INTO kv(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value', [k, JSON.stringify(v)]);
const delKV = (k) => run('DELETE FROM kv WHERE key=?', [k]);

module.exports = { init, q, run, batch, getKV, setKV, delKV };
