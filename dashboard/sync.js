// Datenabruf in kleinen Teilen (jeder Teil ist ein eigener Aufruf, wegen des Vercel-Zeitlimits).
const { q, run, batch, getKV, setKV } = require('./db');
const { gget, loggedInEmail } = require('./google');
const metricool = require('./metricool');

const YT = 'https://www.googleapis.com/youtube/v3';
const AN = 'https://youtubeanalytics.googleapis.com/v2/reports';
const SHORT_MAX_S = 180;
const ymd = (d) => d.toISOString().slice(0, 10);
const daysAgo = (n) => ymd(new Date(Date.now() - n * 86400e3));
const num = (v) => (v == null ? null : Number(v));

function parseDuration(iso) {
  const m = /PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/.exec(iso || '') || [];
  return (+m[1] || 0) * 3600 + (+m[2] || 0) * 60 + (+m[3] || 0);
}
const analytics = (params) => gget('YouTube Analytics', `${AN}?${new URLSearchParams({ ids: 'channel==MINE', ...params })}`);

async function syncChannel() {
  const r = await gget('YouTube Data API', `${YT}/channels?part=snippet,statistics,contentDetails&mine=true`);
  const ch = r.items?.[0];
  if (!ch) throw new Error('YouTube Data API: Zu diesem Konto gehört kein YouTube-Kanal.');
  await setKV('channel', {
    id: ch.id, title: ch.snippet.title, publishedAt: ch.snippet.publishedAt,
    subscribers: +ch.statistics.subscriberCount || 0, hiddenSubs: !!ch.statistics.hiddenSubscriberCount,
    totalViews: +ch.statistics.viewCount || 0, videoCount: +ch.statistics.videoCount || 0,
    uploads: ch.contentDetails.relatedPlaylists.uploads,
  });
}

async function syncVideos() {
  const ch = await getKV('channel');
  if (!ch) throw new Error('Kanal noch nicht geladen.');
  const ids = [];
  let page = '';
  do {
    const r = await gget('YouTube Data API', `${YT}/playlistItems?part=contentDetails&maxResults=50&playlistId=${ch.uploads}${page ? '&pageToken=' + page : ''}`);
    ids.push(...r.items.map((i) => i.contentDetails.videoId));
    page = r.nextPageToken || '';
  } while (page && ids.length < 1000);

  const stmts = [], seen = new Set();
  const sql = `INSERT INTO videos(id,title,thumb,published_at,duration_s,views,likes,comments) VALUES(?,?,?,?,?,?,?,?)
    ON CONFLICT(id) DO UPDATE SET title=excluded.title,thumb=excluded.thumb,published_at=excluded.published_at,duration_s=excluded.duration_s,views=excluded.views,likes=excluded.likes,comments=excluded.comments`;
  for (let i = 0; i < ids.length; i += 50) {
    const r = await gget('YouTube Data API', `${YT}/videos?part=snippet,statistics,contentDetails,status&id=${ids.slice(i, i + 50).join(',')}`);
    for (const v of r.items) {
      const dur = parseDuration(v.contentDetails.duration);
      if (dur > SHORT_MAX_S || v.status?.privacyStatus !== 'public') continue; // nur öffentliche Shorts
      const t = v.snippet.thumbnails;
      seen.add(v.id);
      stmts.push([sql, [v.id, v.snippet.title, (t.medium || t.default || {}).url || null, v.snippet.publishedAt, dur, +v.statistics.viewCount || 0, +v.statistics.likeCount || 0, +v.statistics.commentCount || 0]]);
    }
  }
  for (const row of await q('SELECT id FROM videos')) if (!seen.has(row.id)) stmts.push(['DELETE FROM videos WHERE id=?', [row.id]]);
  await batch(stmts);
}

async function perVideoReport(start, metrics) {
  const rows = [];
  for (let idx = 1; idx <= 1801; idx += 200) {
    const r = await analytics({ startDate: start, endDate: daysAgo(0), dimensions: 'video', metrics, sort: '-views', maxResults: '200', startIndex: String(idx) });
    rows.push(...(r.rows || []));
    if ((r.rows || []).length < 200) break;
  }
  return rows;
}

async function syncAnalytics() {
  const ch = await getKV('channel');
  if (!ch) throw new Error('Kanal noch nicht geladen.');
  const d = await analytics({ startDate: daysAgo(120), endDate: daysAgo(0), dimensions: 'day', metrics: 'views,estimatedMinutesWatched,subscribersGained', sort: 'day' });
  const ins = 'INSERT INTO daily(date,views,minutes,subs) VALUES(?,?,?,?) ON CONFLICT(date) DO UPDATE SET views=excluded.views,minutes=excluded.minutes,subs=excluded.subs';
  const all = await perVideoReport((ch.publishedAt || '2020-01-01').slice(0, 10), 'views,likes,comments,averageViewDuration,averageViewPercentage,subscribersGained');
  await batch([
    ...(d.rows || []).map((r) => [ins, [r[0], r[1], r[2], r[3]]]),
    ...all.map((r) => ['UPDATE videos SET avg_view_s=?, avg_view_pct=?, subs_gained=? WHERE id=?', [num(r[4]), num(r[5]), r[6] ?? 0, r[0]]]),
  ]);
}

async function syncAnalytics90() {
  const last90 = await perVideoReport(daysAgo(90), 'views');
  await batch([['UPDATE videos SET views90=0'], ...last90.map((r) => ['UPDATE videos SET views90=? WHERE id=?', [r[1], r[0]]])]);
}

// Views-Verlauf der ersten Tage (YouTube liefert pro Tag, nicht pro Stunde).
async function videoCurve(id) {
  const v = (await q('SELECT published_at FROM videos WHERE id=?', [id]))[0];
  if (!v) return null;
  const read = () => q('SELECT day_idx,date,views FROM video_daily WHERE video_id=? ORDER BY day_idx', [id]);
  const cached = await read();
  const ageDays = (Date.now() - new Date(v.published_at)) / 86400e3;
  if (cached.length >= 3 || (cached.length && ageDays < 3 && Date.now() - (await getKV('curve_' + id, 0)) < 15 * 60e3)) return cached;
  const start = v.published_at.slice(0, 10);
  const end = ymd(new Date(new Date(start).getTime() + 2 * 86400e3));
  const r = await analytics({ startDate: start, endDate: end > daysAgo(0) ? daysAgo(0) : end, dimensions: 'day', metrics: 'views', filters: `video==${id}`, sort: 'day' });
  await batch((r.rows || []).map((row, i) => ['INSERT INTO video_daily(video_id,day_idx,date,views) VALUES(?,?,?,?) ON CONFLICT(video_id,day_idx) DO UPDATE SET date=excluded.date,views=excluded.views', [id, i, row[0], row[1]]]));
  await setKV('curve_' + id, Date.now());
  return read();
}

async function syncPosts() {
  const posts = await metricool.fetchScheduled();
  await batch([["DELETE FROM posts WHERE source='metricool'"],
    ...posts.map((p) => ['INSERT OR REPLACE INTO posts(id,network,text,start,status,source) VALUES(?,?,?,?,?,?)', [p.id, p.network, p.text, p.start, p.status, p.source]])]);
}

const PARTS = {
  channel: ['Kanal', syncChannel], videos: ['Videos', syncVideos], analytics: ['Analytics', syncAnalytics],
  analytics90: ['Analytics 90 Tage', syncAnalytics90], posts: ['Zeitplan', syncPosts],
};
const NEEDS_LOGIN = new Set(['channel', 'videos', 'analytics', 'analytics90']);

// Führt einen Teil aus. Fehler werden gespeichert (nie ein Absturz) und im Dashboard angezeigt.
async function runPart(name) {
  if (name === 'finish') { await setKV('sync_meta', { lastSync: new Date().toISOString() }); return { ok: true }; }
  const p = PARTS[name]; if (!p) return { ok: false, error: 'Unbekannter Teil' };
  const errors = await getKV('sync_errors', {});
  try {
    if (NEEDS_LOGIN.has(name) && !(await loggedInEmail())) throw new Error('Nicht bei Google eingeloggt.');
    await p[1]();
    delete errors[name];
  } catch (e) { errors[name] = { part: p[0], message: e.message }; }
  await setKV('sync_errors', errors);
  return { ok: !errors[name], error: errors[name]?.message };
}

async function status() {
  const meta = await getKV('sync_meta', {});
  const errors = Object.values(await getKV('sync_errors', {}));
  return { lastSync: meta.lastSync || null, errors, ok: errors.length === 0 };
}

module.exports = { runPart, status, videoCurve, PART_NAMES: Object.keys(PARTS) };
