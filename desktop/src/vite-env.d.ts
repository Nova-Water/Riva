/// <reference types="vite/client" />

interface RivaBridge {
  getBackendUrl: () => Promise<string>;
  onBackendReady: (callback: (baseUrl: string) => void) => void;
  onBackendError: (callback: (message: string) => void) => void;
  openLogsFolder: () => Promise<void>;
  platform: string;
}

interface Window {
  riva?: RivaBridge;
}
