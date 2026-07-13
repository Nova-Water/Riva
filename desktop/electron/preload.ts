/**
 * Preload script: exposes a minimal, safe bridge to the renderer.
 * The renderer never gets direct Node/Electron access — only the backend
 * URL and small event hooks it needs to know when the backend is ready.
 */
import { contextBridge, ipcRenderer } from 'electron';

export interface RivaBridge {
  getBackendUrl: () => Promise<string>;
  onBackendReady: (callback: (baseUrl: string) => void) => void;
  onBackendError: (callback: (message: string) => void) => void;
  openLogsFolder: () => Promise<void>;
  platform: NodeJS.Platform;
}

const bridge: RivaBridge = {
  getBackendUrl: () => ipcRenderer.invoke('riva:get-backend-url'),
  onBackendReady: (callback) => {
    ipcRenderer.on('riva:backend-ready', (_event, baseUrl: string) => callback(baseUrl));
  },
  onBackendError: (callback) => {
    ipcRenderer.on('riva:backend-error', (_event, message: string) => callback(message));
  },
  openLogsFolder: () => ipcRenderer.invoke('riva:open-logs-folder'),
  platform: process.platform,
};

contextBridge.exposeInMainWorld('riva', bridge);
