// Windows console hiding utility
if (process.platform === 'win32') {
  const { spawn } = require('child_process');
  const path = require('path');
  
  // Force hide any console windows that might appear
  const hideConsole = () => {
    // Method 1: Use cmd to hide
    spawn('cmd.exe', ['/c', 'exit'], { 
      stdio: 'ignore', 
      windowsHide: true,
      detached: true
    });
    
    // Method 2: Use PowerShell to hide
    spawn('powershell.exe', ['-Command', 'exit'], { 
      stdio: 'ignore', 
      windowsHide: true,
      detached: true
    });
    
    // Method 3: Set environment variables to prevent console
    process.env.ELECTRON_NO_ATTACH_CONSOLE = 'true';
  };
  
  // Hide console immediately
  hideConsole();
  
  // Also hide on any potential spawn
  const originalSpawn = require('child_process').spawn;
  require('child_process').spawn = function(command, args, options = {}) {
    if (process.platform === 'win32') {
      options.windowsHide = true;
      if (!options.stdio) {
        options.stdio = ['ignore', 'pipe', 'pipe'];
      }
    }
    return originalSpawn.call(this, command, args, options);
  };
}
