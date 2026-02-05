// Import console hiding utility (must be first)
require('./hide-console.js');

const { app, BrowserWindow, ipcMain, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const http = require('http');

// Set up logging - will be initialized after app is ready
let logDir;
let logPath;
let loggingInitialized = false;

function initLogging() {
  if (loggingInitialized) return;
  logDir = path.join(app.getPath('userData'), 'logs');
  logPath = path.join(logDir, 'app.log');
  
  if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir, { recursive: true });
  }
  loggingInitialized = true;
}

function logToFile(level, message) {
  if (!loggingInitialized) initLogging();
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

// Queue system variables
let jobQueue = [];
let isProcessing = false;

    // Process the next job in the queue
    async function processQueue(event) {
      if (isProcessing || jobQueue.length === 0) return;
    
      isProcessing = true;
      const { payload } = jobQueue.shift();
    
      try {
        const {
            city,
            country,
            state,
            theme = 'feature_based',
            mapType = 'city',
            distance = '12000',
            width = '12',
            height = '16',
            format = 'png',
            font = 'Roboto',
            texture = 'none',
            mapShape = 'rectangle',
            artisticEffect = 'none',
            colorEnhancement = 'none',
        } = payload;
    
        logToFile('info', `Generating ${mapType} map for ${city}, ${country} with theme ${theme}`);
        
        // Update UI about queue status
        event.sender.send('queue-update', { 
          active: true, 
          count: jobQueue.length, 
          current: `${city}, ${country}` 
        });
    
        let currentProgress = 0;
        const sendProgress = (pct, text) => {
          try {
            currentProgress = pct;
            event.sender.send('render-progress', { pct, text });
          } catch (_) { }
        };
    
        // Smooth climb between milestones
        const smoothClimb = (targetPct, text) => {
            if (targetPct <= currentProgress) return;
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
            '--map-type', ...(Array.isArray(payload.mapType) ? payload.mapType : [payload.mapType || 'city']),
            '--artistic-effect', payload.artisticEffect,
            '--color-enhancement', payload.colorEnhancement,
            ...(payload.styleRoads ? ['--style-roads', payload.styleRoads] : []),
            ...(payload.styleWater ? ['--style-water', payload.styleWater] : []),
            ...(payload.styleParks ? ['--style-parks', payload.styleParks] : []),
            ...(payload.styleTransit ? ['--style-transit', payload.styleTransit] : []),
        ];
    
        // Determine Python executable path based on environment
        const isPackaged = app.isPackaged;
        let pythonExe;
        if (isPackaged) {
            pythonExe = path.join(process.resourcesPath, 'python', 'Scripts', 'python.exe');
        } else {
            pythonExe = path.join(__dirname, '.venv', 'Scripts', 'python.exe');
        }
    
        if (!fs.existsSync(pythonExe)) {
            pythonExe = 'python';
        }
    
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
    
        sendProgress(5, `Starting: ${city}`);
    
        proc.stdout.on('data', (data) => {
            const chunk = data.toString();
            stdOut += chunk;
            if (chunk.includes('Fetching')) smoothClimb(10, `[${city}] Fetching map data…`);
            if (chunk.includes('Downloading')) smoothClimb(20, `[${city}] Downloading OSM data…`);
            if (chunk.includes('Processing')) smoothClimb(30, `[${city}] Processing geometry…`);
            if (chunk.includes('Rendering')) smoothClimb(45, `[${city}] Rendering layers…`);
            if (chunk.includes('Saving')) smoothClimb(85, `[${city}] Saving image…`);
            if (chunk.includes('Done') || chunk.includes('finished')) smoothClimb(100, `Done: ${city}`);
            event.sender.send('render-log', { type: 'out', chunk });
        });
    
        proc.stderr.on('data', (data) => {
            const chunk = data.toString();
            stdErr += chunk;
            event.sender.send('render-log', { type: 'err', chunk });
        });
    
        await new Promise((pResolve, pReject) => {
            proc.on('close', (code) => {
                if (code === 0) {
                    sendProgress(100, `Done: ${city}`);
                    logToFile('info', `Map generation completed successfully for ${city}, ${country}`);
                    event.sender.send('job-complete', { success: true, city });
                    pResolve();
                } else {
                    sendProgress(0, 'Failed');
                    const errorMsg = stdErr || `Generator exited with code ${code}`;
                    logToFile('error', `Map generation failed for ${city}, ${country}: ${errorMsg}`);
                    event.sender.send('job-complete', { success: false, error: errorMsg, city });
                    pResolve(); // Resolve promise to continue queue even on error
                }
            });
    
            proc.on('error', (err) => {
                sendProgress(0, 'Failed');
                logToFile('error', `Process error: ${err.message}`);
                event.sender.send('job-complete', { success: false, error: err.message, city });
                pResolve();
            });
        });
    
      } catch (error) {
         logToFile('error', `Queue processing error: ${error.message}`);
         event.sender.send('job-complete', { success: false, error: error.message });
      } finally {
        isProcessing = false;
        event.sender.send('queue-update', { 
          active: jobQueue.length > 0, 
          count: jobQueue.length, 
          current: jobQueue.length > 0 ? 'Next job...' : 'Idle' 
        });
        // Trigger next job
        processQueue(event);
      }
    }
    
    ipcMain.handle('generate-map', async (event, payload) => {
        // Add to queue
        jobQueue.push({ payload });
        
        // Notify UI about queue addition
        event.sender.send('queue-update', { 
            active: isProcessing || jobQueue.length > 0, 
            count: jobQueue.length + (isProcessing ? 1 : 0), 
            current: isProcessing ? 'Processing...' : 'Queued'
        });
        
        // Try to trigger processing
        processQueue(event);
        
        return { status: 'queued', position: jobQueue.length };
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
