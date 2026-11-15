// Desktop-Hülle: lädt das gehostete Dashboard. Google-Login läuft im System-Browser
// (Google erlaubt keinen Login in eingebetteten Fenstern), Rückgabe per gravityloop://-Link.
const { app, BrowserWindow, shell, ipcMain } = require('electron');
const path = require('path');
const SCHEME = 'gravityloop';
const APP_URL = (process.env.GL_URL || require('./app-config.json').url).replace(/\/$/, '');
const ORIGIN = new URL(APP_URL).origin;
let win, pending = process.argv.find((a) => a.startsWith(SCHEME + '://'));

if (process.defaultApp) {
  if (process.argv.length >= 2) app.setAsDefaultProtocolClient(SCHEME, process.execPath, [path.resolve(process.argv[1])]);
} else app.setAsDefaultProtocolClient(SCHEME);

if (!app.requestSingleInstanceLock()) app.quit();
const deliver = (url) => { if (win && url) win.webContents.send('deeplink', url); else pending = url; };
app.on('second-instance', (e, argv) => { if (win) { if (win.isMinimized()) win.restore(); win.focus(); } deliver(argv.find((a) => a.startsWith(SCHEME + '://'))); });
app.on('open-url', (e, url) => { e.preventDefault(); deliver(url); });

ipcMain.on('open-external', (e, u) => { try { if (new URL(u).origin === ORIGIN) shell.openExternal(u); } catch {} });
ipcMain.on('retry', () => win && win.loadURL(APP_URL));

function create() {
  win = new BrowserWindow({
    width: 1280, height: 860, minWidth: 380, backgroundColor: '#000000', autoHideMenuBar: true, title: 'Gravity Loop',
    icon: path.join(__dirname, 'build', 'icon.png'),
    webPreferences: { preload: path.join(__dirname, 'preload.js'), contextIsolation: true, nodeIntegration: false, sandbox: true },
  });
  win.loadURL(APP_URL);
  win.webContents.setWindowOpenHandler(({ url }) => { if (/^https?:/.test(url)) shell.openExternal(url); return { action: 'deny' }; });
  win.webContents.on('will-navigate', (e, url) => {
    try { if (new URL(url).origin !== ORIGIN && !url.startsWith('file:')) { e.preventDefault(); if (/^https?:/.test(url)) shell.openExternal(url); } } catch {}
  });
  win.webContents.on('did-fail-load', (e, code, desc, url, isMain) => { if (isMain && code !== -3) win.loadFile(path.join(__dirname, 'offline.html')); });
  win.webContents.on('did-finish-load', () => { if (pending && win.webContents.getURL().startsWith(ORIGIN)) { win.webContents.send('deeplink', pending); pending = null; } });
}
app.whenReady().then(create);
app.on('window-all-closed', () => app.quit());
