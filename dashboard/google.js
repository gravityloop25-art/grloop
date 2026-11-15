const crypto = require('crypto');
const { getKV, setKV, delKV } = require('./db');
const { http, ApiError } = require('./errors');

const SCOPES = [
  'openid', 'email',
  'https://www.googleapis.com/auth/youtube.readonly',
  'https://www.googleapis.com/auth/yt-analytics.readonly',
].join(' ');

const cfg = () => ({
  id: process.env.GOOGLE_CLIENT_ID,
  secret: process.env.GOOGLE_CLIENT_SECRET,
  redirect: process.env.GOOGLE_REDIRECT_URI || 'http://localhost:3000/auth/callback',
  allowed: (process.env.ALLOWED_EMAIL || 'gravity.loop25@gmail.com').toLowerCase(),
});

const configured = () => !!(cfg().id && cfg().secret);

function authUrl(state) {
  const c = cfg();
  const p = new URLSearchParams({
    client_id: c.id, redirect_uri: c.redirect, response_type: 'code', scope: SCOPES,
    access_type: 'offline', prompt: 'consent select_account', state,
    login_hint: c.allowed,
  });
  return 'https://accounts.google.com/o/oauth2/v2/auth?' + p;
}

async function tokenRequest(params) {
  const c = cfg();
  return http('Google-Login', 'https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ client_id: c.id, client_secret: c.secret, ...params }),
  });
}

// Tauscht Code gegen Tokens, prüft die E-Mail und speichert nur bei erlaubtem Konto.
async function handleCallback(code) {
  const c = cfg();
  const t = await tokenRequest({ code, grant_type: 'authorization_code', redirect_uri: c.redirect });
  const info = await http('Google-Login', 'https://openidconnect.googleapis.com/v1/userinfo', {
    headers: { Authorization: 'Bearer ' + t.access_token },
  });
  const email = (info.email || '').toLowerCase();
  if (email !== c.allowed) {
    // Zugriff sofort wieder entziehen, nichts speichern
    fetch('https://oauth2.googleapis.com/revoke?token=' + t.access_token, { method: 'POST' }).catch(() => {});
    throw new ApiError(`Dieses Dashboard ist nur für ${c.allowed} freigegeben (du hast dich mit ${email} angemeldet).`, { status: 403 });
  }
  const prev = getKV('google_tokens', {});
  setKV('google_tokens', {
    email,
    refresh_token: t.refresh_token || prev.refresh_token,
    access_token: t.access_token,
    expires_at: Date.now() + (t.expires_in - 60) * 1000,
  });
  return email;
}

async function accessToken() {
  const t = getKV('google_tokens');
  if (!t) throw new ApiError('Nicht eingeloggt. Bitte mit Google anmelden.', { status: 401 });
  if (t.access_token && t.expires_at > Date.now()) return t.access_token;
  if (!t.refresh_token) throw new ApiError('Login abgelaufen. Bitte neu anmelden.', { status: 401 });
  const r = await tokenRequest({ refresh_token: t.refresh_token, grant_type: 'refresh_token' }).catch((e) => {
    if (e.status === 400 || e.status === 401) { delKV('google_tokens'); throw new ApiError('Login abgelaufen oder widerrufen. Bitte neu anmelden.', { status: 401 }); }
    throw e;
  });
  setKV('google_tokens', { ...t, access_token: r.access_token, expires_at: Date.now() + (r.expires_in - 60) * 1000 });
  return r.access_token;
}

async function gget(source, url) {
  const tok = await accessToken();
  return http(source, url, { headers: { Authorization: 'Bearer ' + tok } });
}

const newState = () => crypto.randomBytes(16).toString('hex');
const loggedInEmail = () => getKV('google_tokens')?.email || null;
const logout = () => delKV('google_tokens');

module.exports = { configured, authUrl, handleCallback, gget, newState, loggedInEmail, logout, cfg };
