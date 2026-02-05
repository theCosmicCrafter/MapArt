const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  generateMap: (payload) => ipcRenderer.invoke('generate-map', payload),
  onRenderProgress: (callback) => ipcRenderer.on('render-progress', (_, data) => callback(data)),
  onQueueUpdate: (callback) => ipcRenderer.on('queue-update', (_, data) => callback(data)),
  onRenderLog: (callback) => ipcRenderer.on('render-log', (_, data) => callback(data)),
  onJobComplete: (callback) => ipcRenderer.on('job-complete', (_, data) => callback(data)),
  getNewestPoster: () => ipcRenderer.invoke('get-newest-poster'),
  openFolder: (folderName) => ipcRenderer.invoke('open-folder', folderName),
});
