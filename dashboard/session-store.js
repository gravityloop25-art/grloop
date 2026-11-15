// Sessions in SQLite, damit der Login einen Neustart/Deploy überlebt.
const { db } = require('./db');
db.exec('CREATE TABLE IF NOT EXISTS sessions (sid TEXT PRIMARY KEY, data TEXT, expires INTEGER)');

function SqliteStore(session) {
  class Store extends session.Store {
    get(sid, cb) {
      const r = db.prepare('SELECT data FROM sessions WHERE sid=? AND expires>?').get(sid, Date.now());
      cb(null, r ? JSON.parse(r.data) : null);
    }
    set(sid, sess, cb) {
      const exp = sess.cookie?.expires ? new Date(sess.cookie.expires).getTime() : Date.now() + 30 * 864e5;
      db.prepare('INSERT INTO sessions(sid,data,expires) VALUES(?,?,?) ON CONFLICT(sid) DO UPDATE SET data=excluded.data,expires=excluded.expires').run(sid, JSON.stringify(sess), exp);
      cb && cb(null);
    }
    destroy(sid, cb) { db.prepare('DELETE FROM sessions WHERE sid=?').run(sid); cb && cb(null); }
    touch(sid, sess, cb) { this.set(sid, sess, cb); }
  }
  setInterval(() => db.prepare('DELETE FROM sessions WHERE expires<?').run(Date.now()), 3600e3).unref();
  return new Store();
}
module.exports = { SqliteStore: function (session) { return SqliteStore(session); } };
