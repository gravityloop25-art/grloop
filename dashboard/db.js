const Database = require('better-sqlite3');
const path = require('path');
const fs = require('fs');

fs.mkdirSync(path.join(__dirname, 'data'), { recursive: true });
const db = new Database(process.env.DB_FILE || path.join(__dirname, 'data', 'dashboard.sqlite'));
db.pragma('journal_mode = WAL');

db.exec(`
CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS videos (
  id TEXT PRIMARY KEY, title TEXT, thumb TEXT, published_at TEXT, duration_s INTEGER,
  views INTEGER DEFAULT 0, likes INTEGER DEFAULT 0, comments INTEGER DEFAULT 0,
  avg_view_s REAL, avg_view_pct REAL, subs_gained INTEGER DEFAULT 0, views90 INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS daily (date TEXT PRIMARY KEY, views INTEGER, minutes REAL, subs INTEGER);
CREATE TABLE IF NOT EXISTS posts (
  id TEXT PRIMARY KEY, network TEXT, text TEXT, start TEXT, status TEXT, source TEXT
);
CREATE TABLE IF NOT EXISTS app_codes (code TEXT PRIMARY KEY, challenge TEXT, expires INTEGER);
CREATE TABLE IF NOT EXISTS video_daily (video_id TEXT, day_idx INTEGER, date TEXT, views INTEGER, PRIMARY KEY (video_id, day_idx));
`);

const getKV = (k, def = null) => {
  const r = db.prepare('SELECT value FROM kv WHERE key=?').get(k);
  return r ? JSON.parse(r.value) : def;
};
const setKV = (k, v) =>
  db.prepare('INSERT INTO kv(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value').run(k, JSON.stringify(v));
const delKV = (k) => db.prepare('DELETE FROM kv WHERE key=?').run(k);

module.exports = { db, getKV, setKV, delKV };
