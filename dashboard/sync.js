const { db, getKV, setKV } = require('./db');
const { gget, loggedInEmail } = require('./google');
const metricool = require('./metricool');

const YT = 'https://www.googleapis.com/youtube/v3';
const AN = 'https://youtubeanalytics.googleapis.com/v2/reports';
const SHORT_MAX_S = 180;
const ymd = (d) => d.toISOString().slice(0, 10);
const daysAgo = (n) => ymd(new Date(Date.now() - n * 86400e3));

function parseDuration(iso) {
  const m = /PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/.exec(iso || '') || [];
  return (+m[1] || 0) * 3600 + (+m[2] || 0) * 60 + (+m[3] || 0);
}

async function analytics(params) {
  const q = new URLSearchParams({ ids: 'channel==MINE', ...params });
  return gget('YouTube Analytics', `${AN}?${q}`);
}

async function syncChannel() {
  const r = await gget('YouTube Data API', `${YT}/channels?part=snippet,statistics,contentDetails&mine=true`);
  const ch = r.items?.[0];
  if (!ch) throw new Error('YouTube Data API: Zu diesem Konto gehört kein YouTube-Kanal.');
  setKV('channel', {
    id: ch.id, title: ch.snippet.title, publishedAt: ch.snippet.publishedAt,
    subscribers: +ch.statistics.subscriberCount || 0, hiddenSubs: !!ch.statistics.hiddenSubscriberCount,
    totalViews: +ch.statistics.viewCount || 0, videoCount: +ch.statistics.videoCount || 0,
    uploads: ch.contentDetails.relatedPlaylists.uploads,
  });
  return getKV('channel');
}

async function syncVideos(ch) {
  const ids = [];
  let page = '';
  do {
    const r = await gget('YouTube Data API', `${YT}/playlistItems?part=contentDetails&maxResults=50&playlistId=${ch.uploads}${page ? '&pageToken=' + page : ''}`);
    ids.push(...r.items.map((i) => i.contentDetails.videoId));
    page = r.nextPageToken || '';
  } while (page && ids.length < 1000);

  const up = db.prepare(`INSERT INTO videos(id,title,thumb,published_at,duration_s,views,likes,comments)
    VALUES(@id,@title,@thumb,@published_at,@duration_s,@views,@likes,@comments)
    ON CONFLICT(id) DO UPDATE SET title=@title,thumb=@thumb,published_at=@published_at,duration_s=@duration_s,views=@views,likes=@likes,comments=@comments`);
  const seen = new Set();
  for (let i = 0; i < ids.length; i += 50) {
    const r = await gget('YouTube Data API', `${YT}/videos?part=snippet,statistics,contentDetails,status&id=${ids.slice(i, i + 50).join(',')}`);
    for (const v of r.items) {
      const dur = parseDuration(v.contentDetails.duration);
      if (dur > SHORT_MAX_S || v.status?.privacyStatus !== 'public') continue; // nur öffentliche Shorts
      const t = v.snippet.thumbnails;
      seen.add(v.id);
      up.run({
        id: v.id, title: v.snippet.title, thumb: (t.medium || t.default || {}).url, published_at: v.snippet.publishedAt,
        duration_s: dur, views: +v.statistics.viewCount || 0, likes: +v.statistics.likeCount || 0, comments: +v.statistics.commentCount || 0,
      });
    }
  }
  // gelöschte/private Videos entfernen
  for (const row of db.prepare('SELECT id FROM videos').all()) if (!seen.has(row.id)) db.prepare('DELETE FROM videos WHERE id=?').run(row.id);
  return seen.size;
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

async function syncAnalytics(ch) {
  // Kanal pro Tag (letzte 120 Tage)
  const d = await analytics({ startDate: daysAgo(120), endDate: daysAgo(0), dimensions: 'day', metrics: 'views,estimatedMinutesWatched,subscribersGained', sort: 'day' });
  const ins = db.prepare('INSERT INTO daily(date,views,minutes,subs) VALUES(?,?,?,?) ON CONFLICT(date) DO UPDATE SET views=excluded.views,minutes=excluded.minutes,subs=excluded.subs');
  db.transaction(() => (d.rows || []).forEach((r) => ins.run(r[0], r[1], r[2], r[3])))();

  // Pro Video, gesamte Laufzeit
  const start = (ch.publishedAt || '2020-01-01').slice(0, 10);
  const all = await perVideoReport(start, 'views,likes,comments,averageViewDuration,averageViewPercentage,subscribersGained');
  const upd = db.prepare('UPDATE videos SET avg_view_s=?, avg_view_pct=?, subs_gained=? WHERE id=?');
  db.transaction(() => all.forEach((r) => upd.run(r[4], r[5], r[6], r[0])))();

  // Pro Video, letzte 90 Tage (für Partnerprogramm-Balken)
  const last90 = await perVideoReport(daysAgo(90), 'views');
  db.prepare('UPDATE videos SET views90=0').run();
  const u90 = db.prepare('UPDATE videos SET views90=? WHERE id=?');
  db.transaction(() => last90.forEach((r) => u90.run(r[1], r[0])))();
}

// Views-Verlauf der ersten Tage eines Videos (YouTube liefert pro Tag, nicht pro Stunde).
async function videoCurve(id) {
  const v = db.prepare('SELECT published_at FROM videos WHERE id=?').get(id);
  if (!v) return null;
  const cached = db.prepare('SELECT day_idx,date,views FROM video_daily WHERE video_id=? ORDER BY day_idx').all(id);
  const ageDays = (Date.now() - new Date(v.published_at)) / 86400e3;
  if (cached.length >= 3 || (cached.length && ageDays < 3 && Date.now() - (getKV('curve_' + id, 0)) < 15 * 60e3)) return cached;
  const start = v.published_at.slice(0, 10);
  const end = ymd(new Date(new Date(start).getTime() + 2 * 86400e3));
  const r = await analytics({ startDate: start, endDate: end > daysAgo(0) ? daysAgo(0) : end, dimensions: 'day', metrics: 'views', filters: `video==${id}`, sort: 'day' });
  const ins = db.prepare('INSERT INTO video_daily(video_id,day_idx,date,views) VALUES(?,?,?,?) ON CONFLICT(video_id,day_idx) DO UPDATE SET date=excluded.date,views=excluded.views');
  db.transaction(() => (r.rows || []).forEach((row, i) => ins.run(id, i, row[0], row[1])))();
  setKV('curve_' + id, Date.now());
  return db.prepare('SELECT day_idx,date,views FROM video_daily WHERE video_id=? ORDER BY day_idx').all(id);
}

async function syncPosts() {
  const posts = await metricool.fetchScheduled();
  db.transaction(() => {
    db.prepare("DELETE FROM posts WHERE source='metricool'").run();
    const ins = db.prepare('INSERT OR REPLACE INTO posts(id,network,text,start,status,source) VALUES(@id,@network,@text,@start,@status,@source)');
    posts.forEach((p) => ins.run(p));
  })();
  return posts.length;
}

let running = false;
async function runSync() {
  if (running) return getKV('sync_status');
  running = true;
  const errors = [];
  const step = async (name, fn) => {
    try { return await fn(); } catch (e) { errors.push({ part: name, message: e.message }); }
  };
  try {
    if (loggedInEmail()) {
      const ch = (await step('Kanal', syncChannel)) || getKV('channel');
      if (ch) {
        await step('Videos', () => syncVideos(ch));
        await step('Analytics', () => syncAnalytics(ch));
      }
    } else {
      errors.push({ part: 'Login', message: 'Nicht bei Google eingeloggt.' });
    }
    await step('Zeitplan', syncPosts);
  } finally {
    running = false;
    setKV('sync_status', { lastSync: new Date().toISOString(), errors, ok: errors.length === 0 });
  }
  return getKV('sync_status');
}

module.exports = { runSync, videoCurve, isRunning: () => running };
