require('dotenv').config({ quiet: true });
const path = require('path');
const express = require('express');
const session = require('express-session');
const { db, getKV } = require('./db');
const google = require('./google');
const { runSync, videoCurve } = require('./sync');
const metricool = require('./metricool');

const DEMO = process.env.DEMO === '1';
const PORT = +process.env.PORT || 3000;
const app = express();
app.disable('x-powered-by');
app.use(session({
  secret: process.env.SESSION_SECRET || require('crypto').randomBytes(24).toString('hex'),
  resave: false, saveUninitialized: false,
  cookie: { httpOnly: true, sameSite: 'lax', maxAge: 30 * 86400e3 },
}));

// ---------- Login ----------
app.get('/auth/login', (req, res) => {
  if (!google.configured()) return res.redirect('/?error=' + encodeURIComponent('GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET fehlen in der .env (siehe README).'));
  req.session.state = google.newState();
  res.redirect(google.authUrl(req.session.state));
});

app.get('/auth/callback', async (req, res) => {
  const fail = (m) => res.redirect('/?error=' + encodeURIComponent(m));
  if (req.query.error) return fail('Login abgebrochen: ' + req.query.error);
  if (!req.query.state || req.query.state !== req.session.state) return fail('Ungültiger Login-Status. Bitte erneut versuchen.');
  try {
    await google.handleCallback(String(req.query.code));
    req.session.ok = true;
    runSync().catch(() => {});
    res.redirect('/');
  } catch (e) {
    fail(e.message);
  }
});

app.post('/auth/logout', (req, res) => { google.logout(); req.session.destroy(() => res.json({ ok: true })); });

// ---------- API ----------
const api = express.Router();
const authed = (req) => DEMO || (req.session.ok && google.loggedInEmail());
api.get('/me', (req, res) => {
  res.json({
    demo: DEMO, loggedIn: !!authed(req), email: DEMO ? 'demo' : google.loggedInEmail(),
    googleConfigured: google.configured(), metricoolConfigured: metricool.configured(),
    allowed: google.cfg().allowed, tz: process.env.TIMEZONE || 'Europe/Berlin',
  });
});
api.use((req, res, next) => (authed(req) ? next() : res.status(401).json({ error: 'Nicht eingeloggt.' })));

api.get('/status', (req, res) => res.json({ ...(getKV('sync_status') || { lastSync: null, errors: [], ok: true }), syncMinutes: +process.env.SYNC_MINUTES || 15 }));
api.post('/sync', async (req, res) => res.json(DEMO ? getKV('sync_status') : await runSync()));

api.get('/overview', (req, res) => {
  const ch = getKV('channel') || {};
  const sum = (n) => db.prepare("SELECT COALESCE(SUM(views),0) v, COALESCE(SUM(minutes),0) m FROM daily WHERE date >= date('now', ?)").get(`-${n} days`);
  const d7 = sum(7), d28 = sum(28), d90 = sum(90);
  const shorts90 = db.prepare('SELECT COALESCE(SUM(views90),0) v FROM videos').get().v;
  res.json({
    channel: ch,
    views7: d7.v, views28: d28.v, views90: d90.v,
    hours7: d7.m / 60, hours28: d28.m / 60, hours90: d90.m / 60,
    partner: { subs: ch.subscribers || 0, subsGoal: 1000, shortsViews90: shorts90, viewsGoal: 10_000_000 },
    daily: db.prepare("SELECT date, views FROM daily WHERE date >= date('now','-90 days') ORDER BY date").all(),
    top: db.prepare('SELECT id,title,thumb,views,likes FROM videos ORDER BY views DESC LIMIT 5').all(),
  });
});

api.get('/videos', (req, res) => res.json(db.prepare('SELECT * FROM videos ORDER BY published_at DESC').all()));

api.get('/videos/:id/curve', async (req, res) => {
  try { res.json({ curve: await videoCurve(req.params.id) || [] }); }
  catch (e) { res.status(502).json({ error: e.message }); }
});

api.get('/schedule', (req, res) => {
  const published = db.prepare('SELECT id,title,published_at,views FROM videos').all()
    .map((v) => ({ id: 'yt-' + v.id, network: 'youtube', text: v.title, start: v.published_at, views: v.views, status: 'published', source: 'youtube' }));
  const planned = db.prepare('SELECT * FROM posts').all();
  res.json({ planned, published, tz: process.env.TIMEZONE || 'Europe/Berlin' });
});

// TikTok-Platzhalter: später hier Metricool-Analytics einhängen
api.get('/tiktok', (req, res) => res.json({ available: false, message: 'TikTok folgt' }));

api.use((err, req, res, next) => res.status(500).json({ error: 'Interner Fehler: ' + err.message }));
app.use('/api', api);

// ---------- Frontend ----------
app.use('/vendor/chart.js', express.static(path.join(__dirname, 'node_modules/chart.js/dist/chart.umd.js')));
app.use(express.static(path.join(__dirname, 'public')));

app.listen(PORT, '127.0.0.1', () => {
  console.log(`Gravity Loop Dashboard: http://localhost:${PORT}${DEMO ? '  (DEMO-MODUS mit Beispieldaten)' : ''}`);
  if (DEMO) return;
  if (!google.configured()) console.log('Hinweis: Google-Zugangsdaten fehlen in .env – siehe README.');
  const minutes = +process.env.SYNC_MINUTES || 15;
  if (google.loggedInEmail() || metricool.configured()) runSync().catch(() => {});
  setInterval(() => runSync().catch(() => {}), minutes * 60e3);
});
