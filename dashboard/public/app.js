const $ = (s, r = document) => r.querySelector(s);
const app = $('#app');
let ME = null, TZ = 'Europe/Berlin';
let charts = [];
const C = { mag: '#ff2bd6', cy: '#00e5ff', or: '#ff8a00', grid: '#23232f', mute: '#8b8b9e' };
const nf = new Intl.NumberFormat('de-DE');
const fmt = (n) => (n == null ? '–' : nf.format(Math.round(n)));
const fmtK = (n) => (n >= 1e6 ? (n / 1e6).toFixed(2).replace('.', ',') + ' Mio' : n >= 1e4 ? (n / 1e3).toFixed(1).replace('.', ',') + ' Tsd' : fmt(n));
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const WD = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag'];

async function api(path, opts) {
  const r = await fetch('/api' + path, opts);
  const j = await r.json().catch(() => ({}));
  if (r.status === 401) { ME.loggedIn = false; route(); throw new Error('login'); }
  if (!r.ok) throw new Error(j.error || 'Fehler ' + r.status);
  return j;
}

// ---- Zeit: alles in Europe/Berlin ----
const partsFmt = new Intl.DateTimeFormat('en-CA', { timeZone: 'Europe/Berlin', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hour12: false, weekday: 'short' });
function local(str) {
  // Metricool liefert lokale Zeit ohne Zone, YouTube UTC mit "Z"
  if (!/[zZ]|[+-]\d\d:?\d\d$/.test(str)) {
    const [d, t = '00:00'] = str.split('T');
    const [h, m] = t.split(':').map(Number);
    const dow = (new Date(d + 'T12:00:00Z').getUTCDay() + 6) % 7;
    return { date: d, h, m, min: h * 60 + m, dow };
  }
  const p = Object.fromEntries(partsFmt.formatToParts(new Date(str)).map((x) => [x.type, x.value]));
  const h = +p.hour % 24, m = +p.minute;
  return { date: `${p.year}-${p.month}-${p.day}`, h, m, min: h * 60 + m, dow: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].indexOf(p.weekday) };
}
const hhmm = (min) => `${String(Math.floor(min / 60)).padStart(2, '0')}:${String(min % 60).padStart(2, '0')}`;
const dateDE = (d) => new Date(d + 'T12:00:00Z').toLocaleDateString('de-DE', { weekday: 'short', day: '2-digit', month: '2-digit', timeZone: 'UTC' });
const todayStr = () => local(new Date().toISOString()).date;
const addDays = (d, n) => new Date(new Date(d + 'T12:00:00Z').getTime() + n * 864e5).toISOString().slice(0, 10);
const mondayOf = (d) => addDays(d, -((new Date(d + 'T12:00:00Z').getUTCDay() + 6) % 7));

function killCharts() { charts.forEach((c) => c.destroy()); charts = []; }
function mkChart(el, cfg) {
  Chart.defaults.color = C.mute; Chart.defaults.font.family = 'system-ui';
  const c = new Chart(el, cfg); charts.push(c); return c;
}
const axes = (extra = {}) => ({ x: { grid: { display: false }, ticks: { maxRotation: 0, autoSkip: true } }, y: { grid: { color: C.grid }, beginAtZero: true, ...extra } });

// ---- Banner / Status ----
function showBanner(items, info) {
  $('#banner').innerHTML = items.map((m) => `<div class="msg ${info ? 'info' : ''}">${esc(m)}</div>`).join('');
}
async function refreshStatus() {
  if (!ME?.loggedIn) { $('#syncInfo').textContent = ''; return; }
  const s = await api('/status').catch(() => null);
  if (!s) return;
  const q = new URLSearchParams(location.search).get('error');
  const msgs = (s.errors || []).map((e) => e.message);
  if (ME.demo) msgs.unshift('DEMO-Modus: Beispieldaten, keine echten Kanaldaten.');
  showBanner(msgs, ME.demo && !s.errors?.length);
  $('#syncInfo').textContent = s.lastSync ? 'Stand ' + new Date(s.lastSync).toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' }) : 'Noch nicht geladen';
}

// ---- Routing ----
async function route() {
  killCharts();
  const p = (location.hash.replace(/^#\/?/, '') || '').split('/')[0];
  document.querySelectorAll('nav a').forEach((a) => a.classList.toggle('on', a.dataset.p === p));
  $('#logoutBtn').hidden = !ME?.loggedIn || ME.demo;
  if (!ME.loggedIn) return loginView();
  app.innerHTML = '<p class="muted">Lade …</p>';
  try {
    await ({ '': overview, videos: videosView, plan: planView, tiktok: tiktokView }[p] || overview)();
  } catch (e) {
    if (e.message !== 'login') app.innerHTML = `<div class="empty"><div class="big">⚠️</div><p>${esc(e.message)}</p></div>`;
  }
}

function loginView() {
  const err = new URLSearchParams(location.search).get('error');
  $('#banner').innerHTML = err ? `<div class="msg">${esc(err)}</div>` : '';
  const setup = !ME.googleConfigured;
  app.innerHTML = `<div class="login card"><h1>Gravity Loop</h1>
    <p class="muted">Dashboard für ${esc(ME.allowed)}</p>
    ${setup ? `<p class="muted">Google-Zugangsdaten fehlen noch. Trage <b>GOOGLE_CLIENT_ID</b> und <b>GOOGLE_CLIENT_SECRET</b> in die <b>.env</b> ein (siehe README) und starte neu.</p>`
      : `<a class="cta" href="/auth/login">Mit Google anmelden</a>`}</div>`;
}

// ---- Seite 1: Übersicht ----
async function overview() {
  const o = await api('/overview');
  const ch = o.channel || {};
  const pct = (a, b) => Math.min(100, (a / b) * 100);
  const k = (n, l, c) => `<div class="card kpi"><div class="n ${c}">${n}</div><div class="l">${l}</div></div>`;
  const subsP = pct(o.partner.subs, o.partner.subsGoal), viewsP = pct(o.partner.shortsViews90, o.partner.viewsGoal);
  app.innerHTML = `
    <h1>${esc(ch.title || 'Übersicht')}</h1>
    <div class="grid kpis">
      ${k(fmt(ch.subscribers), 'Abonnenten', 'c-mag')}
      ${k(fmtK(ch.totalViews || 0), 'Views gesamt', 'c-cy')}
      ${k(fmtK(o.views7), 'Views 7 Tage', 'c-or')}
      ${k(fmtK(o.views28), 'Views 28 Tage', 'c-or')}
      ${k(fmtK(o.views90), 'Views 90 Tage', 'c-or')}
      ${k(fmt(o.hours28) + ' h', 'Watch-Time 28 Tage', 'c-cy')}
    </div>
    <div class="card" style="margin-top:14px">
      <h2>Weg zum Partnerprogramm</h2>
      <div class="barrow"><span>Abonnenten</span><span><b class="c-mag">${fmt(o.partner.subs)}</b> / 1.000</span></div>
      <div class="bar"><i style="width:${subsP}%;background:${C.mag};color:${C.mag}"></i></div>
      <div class="barrow" style="margin-top:14px"><span>Shorts-Views (90 Tage)</span><span><b class="c-cy">${fmtK(o.partner.shortsViews90)}</b> / 10 Mio</span></div>
      <div class="bar"><i style="width:${viewsP}%;background:${C.cy};color:${C.cy}"></i></div>
      <div class="muted" style="font-size:12px">${subsP.toFixed(1).replace('.', ',')} % · ${viewsP.toFixed(1).replace('.', ',')} % geschafft</div>
    </div>
    <div class="grid two" style="margin-top:14px">
      <div class="card"><h2>Views pro Tag (90 Tage)</h2><div class="chartbox"><canvas id="cDaily"></canvas></div></div>
      <div class="card"><h2>Top 5 Videos</h2>${o.top.map((v, i) => `
        <div class="top" data-id="${esc(v.id)}"><span class="rank">${i + 1}</span><img src="${esc(v.thumb)}" alt=""><div class="t">${esc(v.title)}</div><div class="v">${fmtK(v.views)}</div></div>`).join('') || '<p class="muted">Noch keine Videos.</p>'}</div>
    </div>`;
  app.querySelectorAll('.top').forEach((el) => el.onclick = () => openVideo(el.dataset.id));
  const ctx = $('#cDaily').getContext('2d');
  const g = ctx.createLinearGradient(0, 0, 0, 260); g.addColorStop(0, '#ff2bd655'); g.addColorStop(1, '#ff2bd600');
  mkChart($('#cDaily'), {
    type: 'line',
    data: { labels: o.daily.map((d) => dateDE(d.date).replace(/^\S+\s/, '')), datasets: [{ data: o.daily.map((d) => d.views), borderColor: C.mag, backgroundColor: g, fill: true, tension: .3, pointRadius: 0, borderWidth: 2.5 }] },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: axes(), interaction: { intersect: false, mode: 'index' } },
  });
}

// ---- Seite 2: Videos ----
let VIDS = [], sortKey = 'published_at', sortDir = -1, q = '', range = 'all';
const COLS = [
  ['thumb', 'Vorschau', false], ['title', 'Titel', true], ['published_at', 'Veröffentlicht', true], ['views', 'Views', true], ['likes', 'Likes', true],
  ['comments', 'Komm.', true], ['avg_view_s', 'Ø Dauer', true], ['avg_view_pct', 'Bindung', true], ['subs_gained', 'Neue Abos', true],
];
async function videosView() {
  VIDS = await api('/videos');
  app.innerHTML = `<h1>Alle Videos <span class="muted" style="font-size:16px" id="cnt"></span></h1>
    <div class="tools"><input type="search" id="q" placeholder="Suchen …" value="${esc(q)}">
      <select id="range"><option value="all">Alle</option><option value="7">Letzte 7 Tage</option><option value="28">Letzte 28 Tage</option><option value="90">Letzte 90 Tage</option></select>
      <select id="minv"><option value="0">Alle Views</option><option value="1000">≥ 1.000</option><option value="10000">≥ 10.000</option><option value="100000">≥ 100.000</option></select></div>
    <div class="tablewrap"><table><thead><tr>${COLS.map(([k, l, s]) => `<th data-k="${k}" ${s ? '' : 'style="cursor:default"'}>${l}</th>`).join('')}</tr></thead><tbody id="tb"></tbody></table></div>`;
  $('#range').value = range;
  $('#q').oninput = (e) => { q = e.target.value; draw(); };
  $('#range').onchange = (e) => { range = e.target.value; draw(); };
  $('#minv').onchange = draw;
  app.querySelectorAll('th').forEach((th) => th.onclick = () => {
    const k = th.dataset.k; if (k === 'thumb') return;
    sortDir = sortKey === k ? -sortDir : (k === 'title' ? 1 : -1); sortKey = k; draw();
  });
  draw();
}
function draw() {
  const minv = +$('#minv').value;
  const cut = range === 'all' ? 0 : Date.now() - range * 864e5;
  const rows = VIDS.filter((v) => v.title.toLowerCase().includes(q.toLowerCase()) && v.views >= minv && new Date(v.published_at) >= cut)
    .sort((a, b) => { const x = a[sortKey] ?? -1, y = b[sortKey] ?? -1; return (typeof x === 'string' ? x.localeCompare(y) : x - y) * sortDir; });
  $('#cnt').textContent = `(${rows.length})`;
  app.querySelectorAll('th').forEach((th) => th.classList.toggle('s', th.dataset.k === sortKey));
  const dur = (s) => (s == null ? '–' : `${Math.floor(s / 60)}:${String(Math.round(s % 60)).padStart(2, '0')}`);
  $('#tb').innerHTML = rows.map((v) => { const t = local(v.published_at); return `<tr data-id="${esc(v.id)}">
    <td><img class="thumb" src="${esc(v.thumb)}" alt=""></td><td>${esc(v.title)}</td>
    <td>${dateDE(t.date)} ${hhmm(t.min)}</td><td><b>${fmt(v.views)}</b></td><td>${fmt(v.likes)}</td><td>${fmt(v.comments)}</td>
    <td>${dur(v.avg_view_s)}</td><td>${v.avg_view_pct == null ? '–' : v.avg_view_pct.toFixed(0) + ' %'}</td><td>${fmt(v.subs_gained)}</td></tr>`; }).join('')
    || '<tr><td colspan="9" class="muted" style="text-align:center;padding:30px">Keine Treffer.</td></tr>';
  app.querySelectorAll('tbody tr[data-id]').forEach((tr) => tr.onclick = () => openVideo(tr.dataset.id));
}

async function openVideo(id) {
  if (!VIDS.length) VIDS = await api('/videos');
  const v = VIDS.find((x) => x.id === id); if (!v) return;
  const m = $('#modal'); m.hidden = false;
  const t = local(v.published_at);
  m.innerHTML = `<div class="box"><div class="mhead"><img class="thumb" src="${esc(v.thumb)}" alt="">
    <div><h3>${esc(v.title)}</h3><div class="muted">${dateDE(t.date)} · ${hhmm(t.min)} Uhr</div></div><button class="x">✕</button></div>
    <div class="mkpis"><div><b class="c-or">${fmt(v.views)}</b><span class="muted">Views</span></div><div><b class="c-mag">${fmt(v.likes)}</b><span class="muted">Likes</span></div><div><b class="c-cy">${v.avg_view_pct == null ? '–' : v.avg_view_pct.toFixed(0) + ' %'}</b><span class="muted">Bindung</span></div></div>
    <h2>Views: erste 24 h / 48 h</h2><div class="chartbox sm"><canvas id="cCurve"></canvas></div><p class="muted" id="curveNote" style="font-size:12px">Lade …</p>
    <p><a class="muted" target="_blank" rel="noopener" href="https://www.youtube.com/shorts/${esc(v.id)}">Auf YouTube öffnen ↗</a></p></div>`;
  const close = () => { m.hidden = true; m.innerHTML = ''; charts = charts.filter((c) => { if (c.canvas?.id === 'cCurve') { c.destroy(); return false; } return true; }); };
  m.onclick = (e) => { if (e.target === m) close(); }; $('.x', m).onclick = close;
  try {
    const { curve } = await api(`/videos/${encodeURIComponent(id)}/curve`);
    $('#curveNote').textContent = curve.length ? 'YouTube liefert diese Werte nur pro Kalendertag (Tag 1 = Veröffentlichungstag), nicht pro Stunde.' : 'Noch keine Daten (YouTube-Analytics braucht bis zu 2 Tage).';
    const cum = []; curve.reduce((a, r, i) => (cum[i] = a + r.views, cum[i]), 0);
    mkChart($('#cCurve'), { type: 'bar', data: { labels: curve.map((r, i) => `Tag ${i + 1}`), datasets: [
      { label: 'Views am Tag', data: curve.map((r) => r.views), backgroundColor: C.cy, borderRadius: 6 },
      { type: 'line', label: 'Summe', data: cum, borderColor: C.mag, pointBackgroundColor: C.mag, tension: .3 }] },
      options: { responsive: true, maintainAspectRatio: false, scales: axes(), plugins: { legend: { labels: { boxWidth: 12 } } } } });
  } catch (e) { $('#curveNote').textContent = e.message; }
}

// ---- Seite 3: Zeitplan ----
let planMode = 'week', planDate = null, PLAN = null;
const NET = { youtube: 'YouTube', tiktok: 'TikTok', instagram: 'Instagram' };
async function planView() {
  const [s, vids] = await Promise.all([api('/schedule'), api('/videos')]);
  VIDS = vids; PLAN = s; planDate = planDate || todayStr();
  const events = [...s.published, ...s.planned].map((e) => ({ ...e, t: local(e.start) }));
  PLAN.events = events; PLAN.best = bestTimes(vids);
  renderPlan();
}
function bestTimes(vids) {
  const byH = {}, byD = {}, byDH = {};
  vids.forEach((v) => { const t = local(v.published_at);
    [[byH, t.h], [byD, t.dow], [byDH, t.dow * 24 + t.h]].forEach(([o, k]) => { (o[k] ||= []).push(v.views); }); });
  const avg = (a) => a.reduce((x, y) => x + y, 0) / a.length;
  const rank = (o) => Object.entries(o).map(([k, a]) => ({ k: +k, avg: avg(a), n: a.length })).sort((a, b) => b.avg - a.avg);
  return { byH, byD, hours: rank(byH), days: rank(byD), combos: rank(byDH).filter((x) => x.n >= 2) };
}
function renderPlan() {
  killCharts();
  const ev = PLAN.events, today = todayStr();
  const days = planMode === 'week' ? Array.from({ length: 7 }, (_, i) => addDays(mondayOf(planDate), i)) : [planDate];
  const bestH = new Set(PLAN.best.hours.filter((h) => h.n >= 2).slice(0, 3).map((h) => h.k));
  const shift = planMode === 'week' ? 7 : 1;
  const clashes = new Set();
  ev.forEach((a) => ev.forEach((b) => { if (a !== b && a.network === b.network && a.t.date === b.t.date && Math.abs(a.t.min - b.t.min) < 60) clashes.add(a.id); }));
  const nClash = clashes.size;
  const dayHtml = (d) => {
    const list = ev.filter((e) => e.t.date === d).sort((a, b) => a.t.min - b.t.min);
    const nowMin = d === today ? local(new Date().toISOString()).min : (d < today ? 1e9 : -1);
    const free = [];
    for (let h = 8; h <= 22; h++) if (h * 60 > nowMin && !list.some((e) => Math.abs(e.t.min - h * 60) < 60)) free.push(h);
    return `<div class="day ${d === today ? 'today' : ''}"><h4><span>${dateDE(d)}</span><span class="muted">${list.length || ''}</span></h4>
      ${list.map((e) => `<div class="ev ${e.status === 'published' ? 'pub' : 'plan'} ${e.network === 'tiktok' && e.status !== 'published' ? 'tt' : ''} ${clashes.has(e.id) ? 'clash' : ''}">
        <span class="tm">${hhmm(e.t.min)}</span><span class="tag ${esc(e.network)}">${esc(NET[e.network] || e.network)}</span>${clashes.has(e.id) ? ' <span title="Überschneidung: gleiche Plattform &lt; 60 Min Abstand">⚠️</span>' : ''}
        <div class="tx">${esc(e.text)}</div></div>`).join('')}
      ${d >= today ? `<div class="slots">${free.map((h) => `<span class="slot ${bestH.has(h) ? 'best' : ''}" title="${bestH.has(h) ? 'Empfohlene Zeit' : 'Frei'}">${String(h).padStart(2, '0')}:00</span>`).join('')}</div>` : ''}</div>`;
  };
  const B = PLAN.best;
  const rec = B.hours.length ? `<div class="recbox">🎯 <b>Empfehlung:</b> Beste Uhrzeiten ${B.hours.filter((h) => h.n >= 2).slice(0, 3).map((h) => `<b>${String(h.k).padStart(2, '0')}:00</b>`).join(', ') || '–'}
    · beste Tage ${B.days.filter((d) => d.n >= 2).slice(0, 3).map((d) => `<b>${WD[d.k]}</b>`).join(', ') || '–'}
    ${B.combos[0] ? `· Top-Kombi <b>${WD[Math.floor(B.combos[0].k / 24)]} ${String(B.combos[0].k % 24).padStart(2, '0')}:00</b> (Ø ${fmtK(B.combos[0].avg)} Views, ${B.combos[0].n} Videos)` : ''}
    <div class="muted" style="font-size:12px;margin-top:4px">Basis: durchschnittliche Gesamt-Views der Videos nach Veröffentlichungszeit. Ältere Videos haben mehr Zeit gehabt, Views zu sammeln – bei wenigen Videos nur als Richtwert.</div></div>` : '';
  app.innerHTML = `<h1>Upload-Zeitplan</h1>
    <div class="tools"><div class="seg"><button data-m="day" class="${planMode === 'day' ? 'on' : ''}">Tag</button><button data-m="week" class="${planMode === 'week' ? 'on' : ''}">Woche</button></div>
      <button id="prev">‹</button><button id="tod">Heute</button><button id="next">›</button></div>
    <div class="legend"><span><i class="dot" style="background:${C.cy}"></i>Veröffentlicht</span><span><i class="dot" style="background:${C.mag}"></i>Geplant YouTube</span><span><i class="dot" style="background:${C.or}"></i>Geplant TikTok</span><span>⚠️ Überschneidung${nClash ? ` (${nClash})` : ''}</span><span><span class="slot">12:00</span> frei · <span class="slot best">18:00</span> empfohlen</span></div>
    ${PLAN.planned.length ? '' : '<div class="msg info" style="margin:0 0 14px;padding:10px 14px;border:1px solid var(--or);border-radius:12px;color:#ffd7a8">Keine geplanten Posts gefunden. Prüfe METRICOOL_TOKEN in der .env.</div>'}
    <div class="week ${planMode === 'week' ? 'w7' : ''}">${days.map(dayHtml).join('')}</div>
    <h1 style="margin-top:28px">Beste Posting-Zeiten</h1>${rec}
    <div class="rec"><div class="card"><h2>Ø Views nach Wochentag</h2><div class="chartbox sm"><canvas id="cD"></canvas></div></div>
    <div class="card"><h2>Ø Views nach Uhrzeit</h2><div class="chartbox sm"><canvas id="cH"></canvas></div></div></div>`;
  app.querySelectorAll('.seg button').forEach((b) => b.onclick = () => { planMode = b.dataset.m; renderPlan(); });
  $('#prev').onclick = () => { planDate = addDays(planDate, -shift); renderPlan(); };
  $('#next').onclick = () => { planDate = addDays(planDate, shift); renderPlan(); };
  $('#tod').onclick = () => { planDate = todayStr(); renderPlan(); };
  const mean = (a) => (a ? a.reduce((x, y) => x + y, 0) / a.length : 0);
  const opts = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: axes() };
  mkChart($('#cD'), { type: 'bar', data: { labels: WD.map((w) => w.slice(0, 2)), datasets: [{ data: WD.map((_, i) => mean(B.byD[i])), backgroundColor: WD.map((_, i) => (B.days[0]?.k === i ? C.mag : '#ff2bd655')), borderRadius: 6 }] }, options: opts });
  const hrs = Array.from({ length: 24 }, (_, i) => i);
  mkChart($('#cH'), { type: 'bar', data: { labels: hrs, datasets: [{ data: hrs.map((h) => mean(B.byH[h])), backgroundColor: hrs.map((h) => (B.hours[0]?.k === h ? C.cy : '#00e5ff55')), borderRadius: 4 }] }, options: opts });
}

// ---- TikTok ----
async function tiktokView() {
  const t = await api('/tiktok');
  app.innerHTML = `<h1>TikTok</h1><div class="card empty"><div class="big">🎵</div><h2 style="color:var(--or)">TikTok folgt</h2>
    <p>${t.available ? '' : 'Hier erscheinen später Views, Follower und Top-Videos aus Metricool.'}</p>
    <p class="muted" style="font-size:13px">Geplante TikTok-Posts siehst du schon jetzt im Upload-Zeitplan.</p></div>`;
}

// ---- Start ----
$('#syncBtn').onclick = async () => {
  const b = $('#syncBtn'); b.classList.add('spin'); b.firstChild.textContent = '⟳ ';
  try { await api('/sync', { method: 'POST' }); await refreshStatus(); await route(); } catch {} finally { b.classList.remove('spin'); b.firstChild.textContent = '↻ '; }
};
$('#logoutBtn').onclick = async () => { await fetch('/auth/logout', { method: 'POST' }); ME.loggedIn = false; location.href = '/'; };
window.addEventListener('hashchange', route);
(async () => {
  ME = await fetch('/api/me').then((r) => r.json());
  TZ = ME.tz;
  await refreshStatus(); await route();
  setInterval(async () => { if (ME.loggedIn && !document.hidden) { await refreshStatus(); } }, 60e3);
  setInterval(() => { if (ME.loggedIn && !document.hidden && !$('#modal').innerHTML) route(); }, 15 * 60e3);
})();
