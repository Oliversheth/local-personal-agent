const { app, BrowserWindow } = require('electron')
const path = require('path')
const { spawn } = require('child_process')

const startUrl = process.env.NODE_ENV === 'development' 
  ? 'http://localhost:5173'
  : `file://${path.join(__dirname, '../dist/index.html')}`

let backendProcess = null

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1024,
    height: 768,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  })

  mainWindow.loadURL(startUrl)

  // Open DevTools in development
  if (process.env.NODE_ENV === 'development') {
    mainWindow.webContents.openDevTools()
  }
}

function startBackend() {
  if (process.env.NODE_ENV === 'development') {
    // In development, assume backend is started separately
    console.log('Development mode: Backend should be started separately')
    return
  }

  const backendPath = path.join(__dirname, '..', 'backend')
  const pythonPath = path.join(backendPath, 'venv', 'bin', 'python')
  const mainPy = path.join(backendPath, 'main.py')

  backendProcess = spawn(pythonPath, ['-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', '8001'], {
    cwd: backendPath,
    detached: false,
    stdio: 'pipe'
  })

  backendProcess.stdout.on('data', (data) => {
    console.log(`Backend stdout: ${data}`)
  })

  backendProcess.stderr.on('data', (data) => {
    console.log(`Backend stderr: ${data}`)
  })

  backendProcess.on('close', (code) => {
    console.log(`Backend process exited with code ${code}`)
  })
}

app.whenReady().then(() => {
  startBackend()
  createWindow()

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('window-all-closed', function () {
  if (backendProcess) {
    backendProcess.kill()
  }
  if (process.platform !== 'darwin') app.quit()
})

app.on('before-quit', () => {
  if (backendProcess) {
    backendProcess.kill()
  }
})