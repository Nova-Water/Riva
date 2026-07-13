import { app, BrowserWindow, ipcMain, shell } from 'electron';
import path from 'node:path';
import { startBackend, stopBackend } from './backend-manager';

function defaultLogsDirectory(): string {
  // Mirrors backend/app/config.py's default data directory when
  // RIVA_DATA_DIRECTORY is not set.
  return path.join(app.getPath('appData'), 'RIVA AI', 'logs');
}

// electron/tsconfig.json compiles to CommonJS, so __dirname is available natively.
declare const __dirname: string;

const isDev = process.env.NODE_ENV === 'development';

let mainWindow: BrowserWindow | null = null;
let backendBaseUrl = '';

const gotLock = app.requestSingleInstanceLock();
if (!gotLock) {
  app.quit();
} else {
  app.on('second-instance', () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });
}

function createWindow(): void {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 820,
    minWidth: 1024,
    minHeight: 680,
    backgroundColor: '#0a0e1a',
    title: 'RIVA AI — Nova Tech Ltd',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });

  mainWindow.setMenuBarVisibility(false);

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith('http://') || url.startsWith('https://')) {
      shell.openExternal(url);
    }
    return { action: 'deny' };
  });

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools({ mode: 'detach' });
  } else {
    mainWindow.loadFile(path.join(__dirname, '..', 'dist', 'index.html'));
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

ipcMain.handle('riva:get-backend-url', () => backendBaseUrl);
ipcMain.handle('riva:open-logs-folder', async () => {
  const logsDir = process.env.RIVA_DATA_DIRECTORY
    ? path.join(process.env.RIVA_DATA_DIRECTORY, 'logs')
    : defaultLogsDirectory();
  await shell.openPath(logsDir);
});

app.whenReady().then(async () => {
  createWindow();

  try {
    const handle = await startBackend(__dirname, app.isPackaged);
    backendBaseUrl = handle.baseUrl;
    mainWindow?.webContents.send('riva:backend-ready', backendBaseUrl);
  } catch (error) {
    console.error('Failed to start RIVA backend:', error);
    mainWindow?.webContents.send('riva:backend-error', (error as Error).message);
  }

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  stopBackend();
  if (process.platform !== 'darwin') app.quit();
});

app.on('before-quit', () => {
  stopBackend();
});
