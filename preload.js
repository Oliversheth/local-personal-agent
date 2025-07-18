const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  // Backend communication
  sendRequest: (endpoint, data) => ipcRenderer.invoke('api-request', endpoint, data),
  
  // Basic window controls
  closeWindow: () => ipcRenderer.invoke('close-window'),
  minimizeWindow: () => ipcRenderer.invoke('minimize-window'),
  maximizeWindow: () => ipcRenderer.invoke('maximize-window'),
  
  // For future screenshot functionality if needed
  takeScreenshot: () => ipcRenderer.invoke('take-screenshot'),
  
  // App control
  quitApp: () => ipcRenderer.invoke('quit-app')
})