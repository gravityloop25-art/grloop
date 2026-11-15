const { http, ApiError } = require('./errors');

const configured = () => !!process.env.METRICOOL_TOKEN;

const pad = (n) => String(n).padStart(2, '0');
const isoLocal = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;

function normNetwork(n) {
  const s = String(n || '').toLowerCase();
  if (s.includes('youtube')) return 'youtube';
  if (s.includes('tiktok')) return 'tiktok';
  if (s.includes('instagram')) return 'instagram';
  return s || 'unbekannt';
}

// Holt geplante Posts (heute -1 Tag bis +60 Tage). Antwortformat wird tolerant gelesen.
async function fetchScheduled() {
  if (!configured()) throw new ApiError('Metricool: METRICOOL_TOKEN fehlt in den Umgebungsvariablen (.env bzw. Vercel) – geplante Posts können nicht geladen werden.', { source: 'Metricool' });
  const tz = process.env.TIMEZONE || 'Europe/Berlin';
  const from = new Date(Date.now() - 86400e3);
  const to = new Date(Date.now() + 60 * 86400e3);
  const q = new URLSearchParams({
    blogId: process.env.METRICOOL_BLOG_ID || '8100417',
    start: isoLocal(from), end: isoLocal(to), timezone: tz,
  });
  if (process.env.METRICOOL_USER_ID) q.set('userId', process.env.METRICOOL_USER_ID);
  const body = await http('Metricool', 'https://app.metricool.com/api/v2/scheduler/posts?' + q, {
    headers: { 'X-Mc-Auth': process.env.METRICOOL_TOKEN },
  });
  const list = Array.isArray(body) ? body : body.data || body.posts || [];
  const out = [];
  for (const p of list) {
    const dt = p.publicationDate?.dateTime || p.publicationDate || p.date;
    if (!dt) continue;
    const providers = (p.providers || []).map((x) => normNetwork(x.network || x)).filter(Boolean);
    const nets = providers.length ? providers : [normNetwork(p.network)];
    for (const n of nets) {
      out.push({
        id: `mc-${p.id}-${n}`, network: n, text: (p.text || p.title || '').slice(0, 200),
        start: String(dt).slice(0, 19), status: String(p.status || 'PENDING').toLowerCase(), source: 'metricool',
      });
    }
  }
  return out;
}

module.exports = { configured, fetchScheduled };
