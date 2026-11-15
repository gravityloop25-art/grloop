// Zustandslose Login-Cookies (signiert), damit kein Server-Speicher nötig ist (Vercel).
const crypto = require('crypto');
const PROD = process.env.NODE_ENV === 'production' || !!process.env.VERCEL;
const devSecret = crypto.randomBytes(24).toString('hex');
const secret = () => process.env.SESSION_SECRET || devSecret;

function sign(payload) {
  const b = Buffer.from(JSON.stringify(payload)).toString('base64url');
  return b + '.' + crypto.createHmac('sha256', secret()).update(b).digest('base64url');
}
function verify(token) {
  if (!token || !token.includes('.')) return null;
  const [b, m] = token.split('.');
  const want = crypto.createHmac('sha256', secret()).update(b).digest('base64url');
  const a = Buffer.from(m), w = Buffer.from(want);
  if (a.length !== w.length || !crypto.timingSafeEqual(a, w)) return null;
  try { const p = JSON.parse(Buffer.from(b, 'base64url').toString()); return p.exp > Date.now() ? p : null; } catch { return null; }
}
function cookies(req) {
  return Object.fromEntries((req.headers.cookie || '').split(';').map((c) => c.trim().split(/=(.*)/s).slice(0, 2)).filter((x) => x[0]));
}
function setCookie(res, name, value, maxAgeSec) {
  res.append('Set-Cookie', `${name}=${value}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${maxAgeSec}${PROD ? '; Secure' : ''}`);
}
const DAY = 86400;
const login = (res) => setCookie(res, 'gl_s', sign({ ok: 1, exp: Date.now() + 90 * DAY * 1000 }), 90 * DAY);
const isLoggedIn = (req) => !!verify(cookies(req).gl_s)?.ok;
const logout = (res) => setCookie(res, 'gl_s', '', 0);
const setOAuth = (res, data) => setCookie(res, 'gl_o', sign({ ...data, exp: Date.now() + 10 * 60e3 }), 600);
const getOAuth = (req) => verify(cookies(req).gl_o);
const clearOAuth = (res) => setCookie(res, 'gl_o', '', 0);

module.exports = { PROD, login, isLoggedIn, logout, setOAuth, getOAuth, clearOAuth };
