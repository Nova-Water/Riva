/**
 * Starts (or connects to) the RIVA Python backend and waits for it to
 * become healthy before the renderer loads the full interface.
 *
 * Dev mode: spawns `python run.py` from the backend/ directory.
 * Production: spawns the PyInstaller-packaged `riva-backend(.exe)` bundled
 * as an extraResource.
 */
import { ChildProcess, spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import net from 'node:net';
import path from 'node:path';

const DEFAULT_HOST = '127.0.0.1';
const DEFAULT_PORT = 8765;
const HEALTH_TIMEOUT_MS = 30_000;
const HEALTH_POLL_INTERVAL_MS = 500;

let backendProcess: ChildProcess | null = null;

function isPortFree(port: number, host: string): Promise<boolean> {
  return new Promise((resolve) => {
    const server = net.createServer();
    server.once('error', () => resolve(false));
    server.once('listening', () => server.close(() => resolve(true)));
    server.listen(port, host);
  });
}

async function findAvailablePort(preferred: number, host: string): Promise<number> {
  if (await isPortFree(preferred, host)) return preferred;
  for (let port = preferred + 1; port < preferred + 50; port++) {
    if (await isPortFree(port, host)) return port;
  }
  throw new Error('Could not find an available port for the RIVA backend.');
}

async function isHealthy(baseUrl: string): Promise<boolean> {
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 2000);
    const resp = await fetch(`${baseUrl}/health`, { signal: controller.signal });
    clearTimeout(timeout);
    return resp.ok;
  } catch {
    return false;
  }
}

function waitForHealth(baseUrl: string, timeoutMs: number): Promise<boolean> {
  const start = Date.now();
  return new Promise((resolve) => {
    const poll = async () => {
      if (await isHealthy(baseUrl)) {
        resolve(true);
        return;
      }
      if (Date.now() - start > timeoutMs) {
        resolve(false);
        return;
      }
      setTimeout(poll, HEALTH_POLL_INTERVAL_MS);
    };
    poll();
  });
}

export interface BackendHandle {
  baseUrl: string;
  alreadyRunning: boolean;
}

export async function startBackend(appRoot: string, isPackaged: boolean): Promise<BackendHandle> {
  const host = process.env.BACKEND_HOST || DEFAULT_HOST;
  const preferredPort = Number(process.env.BACKEND_PORT || DEFAULT_PORT);

  const existingBaseUrl = `http://${host}:${preferredPort}`;
  if (await isHealthy(existingBaseUrl)) {
    // A backend (likely started manually for development) is already serving this port.
    return { baseUrl: existingBaseUrl, alreadyRunning: true };
  }

  const port = await findAvailablePort(preferredPort, host);
  const baseUrl = `http://${host}:${port}`;

  if (isPackaged) {
    const exeName = process.platform === 'win32' ? 'riva-backend.exe' : 'riva-backend';
    const exePath = path.join(process.resourcesPath, 'backend', exeName);
    if (!existsSync(exePath)) {
      throw new Error(`Backend executable not found at ${exePath}`);
    }
    backendProcess = spawn(exePath, [], {
      env: { ...process.env, BACKEND_HOST: host, BACKEND_PORT: String(port) },
      stdio: 'pipe',
    });
  } else {
    const backendDir = path.join(appRoot, '..', 'backend');
    const pythonBin = process.platform === 'win32' ? 'python' : 'python3';
    backendProcess = spawn(pythonBin, ['run.py'], {
      cwd: backendDir,
      env: { ...process.env, BACKEND_HOST: host, BACKEND_PORT: String(port) },
      stdio: 'pipe',
    });
  }

  backendProcess.stdout?.on('data', (data) => process.stdout.write(`[backend] ${data}`));
  backendProcess.stderr?.on('data', (data) => process.stderr.write(`[backend] ${data}`));
  backendProcess.on('exit', (code) => {
    console.log(`[backend] process exited with code ${code}`);
    backendProcess = null;
  });

  const healthy = await waitForHealth(baseUrl, HEALTH_TIMEOUT_MS);
  if (!healthy) {
    throw new Error(
      'The RIVA backend did not start in time. Check that Python and its dependencies are installed correctly.'
    );
  }

  return { baseUrl, alreadyRunning: false };
}

export function stopBackend(): void {
  if (backendProcess && !backendProcess.killed) {
    backendProcess.kill();
    backendProcess = null;
  }
}
