require('dotenv').config({ quiet: true });
const path = require('path');
const crypto = require('crypto');
const express = require('express');
const { q, run, getKV } = require('./db');
const google = require('./google');
const sess = require('./session');
const { runPart, status, videoCurve } = require('./sync');
const metricool = require('./metricool');

const DEMO = process.env.DEMO === '1';
const PORT = +process.env.PORT || 3000;
const HOST = process.env.HOST || '127.0.0.1';
if (sess.PROD && !process.env.SESSION_SECRET) console.error('WARNUNG: SESSION_SECRET fehlt – Logins gehen verloren. Bitte in den Umgebungsvariablen setzen.');

const app = express();
app.disable('x-powered-by');
app.set('trust proxy', 1);
app.get('/healthz', (req, res) => res.send('ok'));

// ---------- Login ----------
app.get('/auth/login', (req, res) => {
  if (!google.configured()) return res.redirect('/?error=' + encodeURIComponent('GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET fehlen in den Umgebungsvariablen (siehe README).'));
  const state = google.newState();
  // App-Login (Desktop/Android): Login im System-Browser, Rückgabe per Einmal-Code + PKCE-Challenge
  const challenge = req.query.app === '1' && /^[a-f0-9]{64}$/.test(String(req.query.challenge || '')) ? String(req.query.challenge) : null;
  sess.setOAuth(res, { state, challenge });
  res.redirect(google.authUrl(state));
});

app.get('/auth/callback', async (req, res) => {
  const fail = (m) => res.redirect('/?error=' + encodeURIComponent(m));
  const o = sess.getOAuth(req);
  sess.clearOAuth(res);
  if (req.query.error) return fail('Login abgebrochen: ' + req.query.error);
  if (!o || !req.query.state || req.query.state !== o.state) return fail('Ungültiger Login-Status. Bitte erneut versuchen.');
  try {
    await google.handleCallback(String(req.query.code));
  } catch (e) { return fail(e.message); }
  if (o.challenge) {
    const code = crypto.randomBytes(24).toString('hex');
    await run('INSERT INTO app_codes(code,challenge,expires) VALUES(?,?,?)', [code, o.challenge, Date.now() + 120e3]);
    const link = `gravityloop://login?code=${code}`;
    return res.type('html').send(`<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1"><body style="background:#000;color:#fff;font:18px system-ui;text-align:center;padding:15vh 20px"><h2>Login erfolgreich ✔</h2><p><a style="display:inline-block;background:#ff2bd6;color:#000;font-weight:800;padding:14px 26px;border-radius:12px;text-decoration:none" href="${link}">Zurück zur App</a></p><p style="color:#888">Du kannst dieses Fenster danach schließen.</p><script>setTimeout(function(){location.href=${JSON.stringify(link)}},300)</script>`);
  }
  sess.login(res);
  res.redirect('/');
});

// Löst den Einmal-Code aus der App ein (nur mit passendem Verifier, 2 Minuten gültig, einmalig).
app.get('/auth/exchange', async (req, res) => {
  const code = String(req.query.code || '');
  const row = (await q('SELECT * FROM app_codes WHERE code=?', [code]))[0];
  await run('DELETE FROM app_codes WHERE code=? OR expires<?', [code, Date.now()]);
  const ok = row && row.expires > Date.now() && (await google.loggedInEmail()) &&
    crypto.createHash('sha256').update(String(req.query.verifier || '')).digest('hex') === row.challenge;
  if (!ok) return res.redirect('/?error=' + encodeURIComponent('App-Login fehlgeschlagen oder abgelaufen. Bitte erneut anmelden.'));
  sess.login(res);
  res.redirect('/');
});

app.post('/auth/logout', (req, res) => { sess.logout(res); res.json({ ok: true }); });

// ---------- API ----------
const api = express.Router();
const authed = async (req) => DEMO || (sess.isLoggedIn(req) && !!(await google.loggedInEmail()));
const tz = () => process.env.TIMEZONE || 'Europe/Berlin';

api.get('/me', async (req, res) => {
  const ok = await authed(req);
  if (ok && !DEMO) sess.login(res); // Cookie verlängern
  res.json({
    demo: DEMO, loggedIn: !!ok, email: DEMO ? 'demo' : (ok ? await google.loggedInEmail() : null),
    googleConfigured: google.configured(), metricoolConfigured: metricool.configured(),
    allowed: google.cfg().allowed, tz: tz(),
  });
});
api.use(async (req, res, next) => ((await authed(req)) ? next() : res.status(401).json({ error: 'Nicht eingeloggt.' })));

api.get('/status', async (req, res) => res.json({ ...(await status()), syncMinutes: +process.env.SYNC_MINUTES || 15 }));
api.post('/sync', async (req, res) => res.json(DEMO ? { ok: true } : await runPart(String(req.query.part || ''))));

api.get('/overview', async (req, res) => {
  const ch = (await getKV('channel')) || {};
  const sum = async (n) => (await q("SELECT COALESCE(SUM(views),0) v, COALESCE(SUM(minutes),0) m FROM daily WHERE date >= date('now', ?)", [`-${n} days`]))[0];
  const [d7, d28, d90] = [await sum(7), await sum(28), await sum(90)];
  const shorts90 = (await q('SELECT COALESCE(SUM(views90),0) v FROM videos'))[0].v;
  res.json({
    channel: ch,
    views7: d7.v, views28: d28.v, views90: d90.v,
    hours7: d7.m / 60, hours28: d28.m / 60, hours90: d90.m / 60,
    partner: { subs: ch.subscribers || 0, subsGoal: 1000, shortsViews90: shorts90, viewsGoal: 10_000_000 },
    daily: await q("SELECT date, views FROM daily WHERE date >= date('now','-90 days') ORDER BY date"),
    top: await q('SELECT id,title,thumb,views,likes FROM videos ORDER BY views DESC LIMIT 5'),
  });
});

api.get('/videos', async (req, res) => res.json(await q('SELECT * FROM videos ORDER BY published_at DESC')));

api.get('/videos/:id/curve', async (req, res) => {
  try { res.json({ curve: (await videoCurve(req.params.id)) || [] }); }
  catch (e) { res.status(502).json({ error: e.message }); }
});

api.get('/schedule', async (req, res) => {
  const published = (await q('SELECT id,title,published_at,views FROM videos'))
    .map((v) => ({ id: 'yt-' + v.id, network: 'youtube', text: v.title, start: v.published_at, views: v.views, status: 'published', source: 'youtube' }));
  res.json({ planned: await q('SELECT * FROM posts'), published, tz: tz() });
});

// TikTok-Platzhalter: später hier Metricool-Analytics einhängen
api.get('/tiktok', (req, res) => res.json({ available: false, message: 'TikTok folgt' }));

api.use((err, req, res, next) => res.status(500).json({ error: 'Interner Fehler: ' + err.message }));
app.use('/api', api);

// ---------- Frontend (lokal; auf Vercel liefert das CDN public/) ----------
app.use(express.static(path.join(__dirname, 'public')));

module.exports = app;

if (require.main === module) {
  app.listen(PORT, HOST, () => {
    console.log(`Gravity Loop Dashboard: http://${HOST}:${PORT}${DEMO ? '  (DEMO-Modus mit Beispieldaten)' : ''}`);
    if (!DEMO && !google.configured()) console.log('Hinweis: Google-Zugangsdaten fehlen in .env – siehe README.');
  });
}
