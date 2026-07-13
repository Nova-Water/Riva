import { useEffect } from 'react';
import { api } from '../services/api';
import { useAssistantStore } from '../stores/useAssistantStore';

const POLL_INTERVAL_MS = 5000;
const MAX_STARTUP_ATTEMPTS = 40;

export function useBackendConnection(): void {
  const setBackendConnected = useAssistantStore((s) => s.setBackendConnected);
  const setBackendError = useAssistantStore((s) => s.setBackendError);

  useEffect(() => {
    let cancelled = false;

    if (window.riva) {
      window.riva.onBackendReady(() => {
        if (!cancelled) setBackendConnected();
      });
      window.riva.onBackendError((message) => {
        if (!cancelled) setBackendError(message);
      });
    }

    async function attemptConnect(): Promise<void> {
      for (let attempt = 0; attempt < MAX_STARTUP_ATTEMPTS; attempt++) {
        if (cancelled) return;
        try {
          await api.health();
          if (!cancelled) await setBackendConnected();
          return;
        } catch {
          await new Promise((resolve) => setTimeout(resolve, 1000));
        }
      }
      if (!cancelled) {
        setBackendError('RIVA could not connect to its backend service after multiple attempts.');
      }
    }

    attemptConnect();

    const pollHandle = setInterval(async () => {
      try {
        await api.health();
      } catch {
        if (!cancelled) setBackendError('Lost connection to the RIVA backend.');
      }
    }, POLL_INTERVAL_MS);

    return () => {
      cancelled = true;
      clearInterval(pollHandle);
    };
  }, [setBackendConnected, setBackendError]);
}
