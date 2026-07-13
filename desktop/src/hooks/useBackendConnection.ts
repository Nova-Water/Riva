import { useEffect } from 'react';
import { api } from '../services/api';
import { useAssistantStore } from '../stores/useAssistantStore';

const POLL_INTERVAL_MS = 5000;
const STARTUP_RETRY_INTERVAL_MS = 1000;
// A packaged PyInstaller backend can take well over 30s to self-extract and
// import heavy dependencies (faster-whisper, ctranslate2) on its first launch.
const MAX_STARTUP_ATTEMPTS = 60;
// Require a few consecutive failed health checks before declaring the
// connection lost, so a single slow/transient request doesn't flip the
// whole UI into an error state.
const CONSECUTIVE_FAILURES_BEFORE_ERROR = 3;

export function useBackendConnection(): void {
  const setBackendConnected = useAssistantStore((s) => s.setBackendConnected);
  const setBackendError = useAssistantStore((s) => s.setBackendError);

  useEffect(() => {
    let cancelled = false;
    let pollHandle: ReturnType<typeof setInterval> | undefined;
    let consecutiveFailures = 0;

    if (window.riva) {
      window.riva.onBackendReady(() => {
        if (!cancelled) setBackendConnected();
      });
      window.riva.onBackendError((message) => {
        if (!cancelled) setBackendError(message);
      });
    }

    function startPolling(): void {
      if (pollHandle) return;
      pollHandle = setInterval(async () => {
        try {
          await api.health();
          consecutiveFailures = 0;
          // Recover automatically if the backend comes back after a blip.
          if (!cancelled) setBackendConnected();
        } catch {
          consecutiveFailures += 1;
          if (!cancelled && consecutiveFailures >= CONSECUTIVE_FAILURES_BEFORE_ERROR) {
            setBackendError('Lost connection to the RIVA backend.');
          }
        }
      }, POLL_INTERVAL_MS);
    }

    async function attemptConnect(): Promise<void> {
      for (let attempt = 0; attempt < MAX_STARTUP_ATTEMPTS; attempt++) {
        if (cancelled) return;
        try {
          await api.health();
          if (!cancelled) {
            await setBackendConnected();
            startPolling();
          }
          return;
        } catch {
          await new Promise((resolve) => setTimeout(resolve, STARTUP_RETRY_INTERVAL_MS));
        }
      }
      if (!cancelled) {
        setBackendError('RIVA could not connect to its backend service after multiple attempts.');
        // Keep trying in the background in case the backend is just slow to start.
        startPolling();
      }
    }

    attemptConnect();

    return () => {
      cancelled = true;
      if (pollHandle) clearInterval(pollHandle);
    };
  }, [setBackendConnected, setBackendError]);
}
