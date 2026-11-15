// Übersetzt API-Fehler in verständliche deutsche Meldungen.
class ApiError extends Error {
  constructor(message, { status, source } = {}) {
    super(message);
    this.status = status;
    this.source = source;
  }
}

function explain(source, status, body) {
  const text = typeof body === 'string' ? body : JSON.stringify(body || {});
  if (/quotaExceeded|rateLimitExceeded|dailyLimitExceeded/i.test(text))
    return `${source}: Tageslimit (Quota) erreicht. Die Daten werden morgen automatisch wieder geladen – bis dahin siehst du die zuletzt gespeicherten Werte.`;
  if (/accessNotConfigured|has not been used|is disabled|SERVICE_DISABLED/i.test(text))
    return `${source}: Die API ist im Google-Cloud-Projekt nicht aktiviert. Bitte in der Cloud Console „YouTube Data API v3“ und „YouTube Analytics API“ aktivieren (siehe README).`;
  if (status === 401) return `${source}: Zugriff abgelehnt (401). Bitte neu einloggen bzw. Token bzw. Umgebungsvariablen prüfen.`;
  if (status === 403) return `${source}: Keine Berechtigung (403). Prüfe Login-Konto, Freigaben und API-Aktivierung.`;
  if (status === 404) return `${source}: Nicht gefunden (404). Prüfe die IDs in den Umgebungsvariablen.`;
  if (status === 429) return `${source}: Zu viele Anfragen (429). Es wird beim nächsten Durchlauf erneut versucht.`;
  if (status >= 500) return `${source}: Der Dienst hat gerade ein Problem (${status}). Später erneut versuchen.`;
  return `${source}: Unerwarteter Fehler (${status}).`;
}

async function http(source, url, opts = {}) {
  let res;
  try {
    res = await fetch(url, opts);
  } catch (e) {
    throw new ApiError(`${source}: Keine Verbindung (${e.cause?.code || e.message}). Internet prüfen.`, { source });
  }
  const raw = await res.text();
  let body;
  try { body = JSON.parse(raw); } catch { body = raw; }
  if (!res.ok) throw new ApiError(explain(source, res.status, body), { status: res.status, source });
  return body;
}

module.exports = { ApiError, http };
