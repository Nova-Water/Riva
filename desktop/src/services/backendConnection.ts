/**
 * Resolves the RIVA backend's base URL. Inside Electron this comes from the
 * main process (which knows the actual port it started the backend on).
 * When running the renderer standalone in a browser (e.g. `vite` alone,
 * or component tests) we fall back to the documented default.
 */
const FALLBACK_BASE_URL = 'http://127.0.0.1:8765';

let resolvedBaseUrl: string | null = null;
let resolvePromise: Promise<string> | null = null;

export function getBackendBaseUrl(): Promise<string> {
  if (resolvedBaseUrl) return Promise.resolve(resolvedBaseUrl);
  if (resolvePromise) return resolvePromise;

  resolvePromise = new Promise((resolve) => {
    if (window.riva) {
      window.riva.getBackendUrl().then((url) => {
        const finalUrl = url || FALLBACK_BASE_URL;
        resolvedBaseUrl = finalUrl;
        resolve(finalUrl);
      });
      window.riva.onBackendReady((url) => {
        resolvedBaseUrl = url;
      });
    } else {
      resolvedBaseUrl = FALLBACK_BASE_URL;
      resolve(FALLBACK_BASE_URL);
    }
  });

  return resolvePromise;
}

export function setBackendBaseUrlForTesting(url: string): void {
  resolvedBaseUrl = url;
  resolvePromise = Promise.resolve(url);
}
