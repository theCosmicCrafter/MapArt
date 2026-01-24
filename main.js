const { app, BrowserWindow, ipcMain, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const http = require('http');

// Import console hiding utility (must be first)
require('./hide-console.js');

// Set up logging
const logDir = path.join(__dirname, 'logs');
const logPath = path.join(logDir, 'app.log');

if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir, { recursive: true });
}

function logToFile(level, message) {
  const timestamp = new Date().toISOString();
  const logMessage = `${timestamp} - ${level.toUpperCase()} - ${message}\n`;
  fs.appendFileSync(logPath, logMessage);
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1280,
    height: 900,
    minWidth: 1000,
    minHeight: 700,
    backgroundColor: '#050505',
    autoHideMenuBar: true,
    webPreferences: {
      contextIsolation: true,
      sandbox: true,
      preload: path.join(__dirname, 'preload.js'),
    },
  });

  win.loadFile(path.join(__dirname, 'ui_hightech.html'));
  
  // Open DevTools in development
  if (process.env.NODE_ENV === 'development') {
    win.webContents.openDevTools();
  }
}

ipcMain.handle('generate-map', async (event, payload) => {
  const {
    city,
    country,
    state,
    theme = 'feature_based',
    distance = '29000',
    width = '12',
    height = '16',
    format = 'png',
    font = 'Roboto',
    texture = 'none',
    mapShape = 'rectangle',
    artisticEffect = 'none',
    colorEnhancement = 'none',
  } = payload;
  
  logToFile('info', `Generating map for ${city}, ${country} with theme ${theme}`);
  
  return new Promise((resolve, reject) => {
    let currentProgress = 0;
    const sendProgress = (pct, text) => {
      try {
        currentProgress = pct;
        event.sender.send('render-progress', { pct, text });
      } catch (_) {
        // ignore send errors
      }
    };
    // Smooth climb between milestones
    const smoothClimb = (targetPct, text) => {
      if (targetPct <= currentProgress) return;
      const steps = Math.ceil((targetPct - currentProgress) / 2);
      let step = 1;
      const interval = setInterval(() => {
        const next = Math.min(currentProgress + 2, targetPct);
        sendProgress(next, text);
        if (next >= targetPct) clearInterval(interval);
      }, 150);
    };

    const args = [
      'create_map_poster.py',
      '--city', payload.city,
      '--country', payload.country,
      ...(state ? ['--state', state] : []),
      '--distance', payload.distance,
      '--width', payload.width,
      '--height', payload.height,
      '--format', payload.format,
      '--theme', payload.theme,
      '--font', payload.font,
      '--texture', payload.texture,
      '--map-shape', payload.mapShape || 'rectangle',
      '--artistic-effect', payload.artisticEffect,
      '--color-enhancement', payload.colorEnhancement,
    ];

    const pythonExe = process.platform === 'win32' ? path.join(__dirname, '.venv', 'Scripts', 'python.exe') : 'python';
    const env = { ...process.env, PYTHONIOENCODING: 'utf-8' };
    const proc = spawn(pythonExe, args, { 
      cwd: __dirname, 
      shell: false, 
      env, 
      windowsHide: true,
      stdio: ['ignore', 'pipe', 'pipe']
    });

    let stdOut = '';
    let stdErr = '';

    sendProgress(5, 'Starting generator…');

    proc.stdout.on('data', (data) => {
      const chunk = data.toString();
      stdOut += chunk;
      // Fine-grained progress based on keywords
      if (chunk.includes('Fetching')) smoothClimb(10, 'Fetching map data…');
      if (chunk.includes('Downloading')) smoothClimb(20, 'Downloading OSM data…');
      if (chunk.includes('Processing')) smoothClimb(30, 'Processing geometry…');
      if (chunk.includes('Rendering')) smoothClimb(45, 'Rendering layers…');
      if (chunk.includes('Saving')) smoothClimb(85, 'Saving image…');
      if (chunk.includes('Done') || chunk.includes('finished')) smoothClimb(100, 'Done. Saved to /outputs');
      event.sender.send('render-log', { type: 'out', chunk });
    });

    proc.stderr.on('data', (data) => {
      const chunk = data.toString();
      stdErr += chunk;
      event.sender.send('render-log', { type: 'err', chunk });
    });

    proc.on('close', (code) => {
      if (code === 0) {
        sendProgress(100, 'Done. Saved to /outputs');
        logToFile('info', `Map generation completed successfully for ${city}, ${country}`);
        resolve({ ok: true, output: stdOut.trim() });
      } else {
        sendProgress(0, 'Failed');
        const errorMsg = stdErr || `Generator exited with code ${code}`;
        logToFile('error', `Map generation failed for ${city}, ${country}: ${errorMsg}`);
        reject(new Error(errorMsg));
      }
    });

    proc.on('error', (err) => {
      sendProgress(0, 'Failed');
      logToFile('error', `Process error: ${err.message}`);
      reject(err);
    });
  });
});

ipcMain.handle('get-newest-poster', async () => {
  const outputsDir = path.join(__dirname, 'outputs');
  if (!fs.existsSync(outputsDir)) return null;
  const files = fs.readdirSync(outputsDir).filter(f => f.endsWith('.png'));
  if (files.length === 0) return null;
  const newest = files
    .map(f => ({ file: f, mtime: fs.statSync(path.join(outputsDir, f)).mtime }))
    .sort((a, b) => b.mtime - a.mtime)[0];
  return path.join(outputsDir, newest.file);
});

ipcMain.handle('open-folder', async (event, folderName) => {
  const folderPath = path.join(__dirname, folderName);
  if (fs.existsSync(folderPath)) {
    await shell.openPath(folderPath);
  } else {
    throw new Error(`Folder ${folderName} does not exist`);
  }
});

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
