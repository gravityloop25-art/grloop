const { contextBridge, ipcRenderer } = require('electron');
contextBridge.exposeInMainWorld('glApp', {
  openExternal: (u) => ipcRenderer.send('open-external', u),
  onDeepLink: (cb) => ipcRenderer.on('deeplink', (e, u) => cb(u)),
  retry: () => ipcRenderer.send('retry'),
});
