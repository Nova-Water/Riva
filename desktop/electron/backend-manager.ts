/**
 * Starts (or connects to) the RIVA Python backend and waits for it to
 * become healthy before the renderer loads the full interface.
 *
 * Dev mode: spawns `python run.py` from the backend/ directory.
 * Production: spawns the PyInstaller-packaged `riva-backend(.exe)` bundled
 * as an extraResource.
 *
 * A packaged Electron app has no visible console on Windows, so the
 * backend's stdout/stderr (and any spawn failure) would otherwise be
 * completely invisible to the user. Everything here is also mirrored to a
 * `backend-launch.log` file so a failed launch can actually be diagnosed.
 */
import { app } from 'electron';
import { ChildProcess, spawn } from 'node:child_process';
import { existsSync, mkdirSync, WriteStream, createWriteStream } from 'node:fs';
import net from 'node:net';
import path from 'node:path';

const DEFAULT_HOST = '127.0.0.1';
const DEFAULT_PORT = 8765;
// A packaged PyInstaller backend can take well over 30s to self-extract and
// import heavy dependencies (faster-whisper, ctranslate2) on its first launch.
const HEALTH_TIMEOUT_MS = 60_000;
const HEALTH_POLL_INTERVAL_MS = 500;
// Give a spawned process a brief moment to fail fast (e.g. ENOENT, blocked by
// antivirus) before we commit to the full health-check polling window.
const SPAWN_SETTLE_MS = 300;

let backendProcess: ChildProcess | null = null;
let launchLogStream: WriteStream | null = null;

/** Mirrors backend/app/config.py's default data directory when RIVA_DATA_DIRECTORY is not set. */
export function defaultDataDirectory(): string {
  return process.env.RIVA_DATA_DIRECTORY || path.join(app.getPath('appData'), 'RIVA AI');
}

export function logsDirectory(): string {
  return path.join(defaultDataDirectory(), 'logs');
}

function openLaunchLog(): WriteStream {
  const dir = logsDirectory();
  mkdirSync(dir, { recursive: true });
  const stream = createWriteStream(path.join(dir, 'backend-launch.log'), { flags: 'a' });
  stream.write(`\n----- RIVA launch at ${new Date().toISOString()} -----\n`);
  return stream;
}

function logLine(line: string): void {
  console.log(line);
  launchLogStream?.write(line.endsWith('\n') ? line : `${line}\n`);
}

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

function waitForHealth(baseUrl: string, timeoutMs: number, hasExited: () => boolean): Promise<boolean> {
  const start = Date.now();
  return new Promise((resolve) => {
    const poll = async () => {
      if (await isHealthy(baseUrl)) {
        resolve(true);
        return;
      }
      if (hasExited() || Date.now() - start > timeoutMs) {
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
  launchLogStream = openLaunchLog();

  const host = process.env.BACKEND_HOST || DEFAULT_HOST;
  const preferredPort = Number(process.env.BACKEND_PORT || DEFAULT_PORT);
  const logPath = path.join(logsDirectory(), 'backend-launch.log');

  const existingBaseUrl = `http://${host}:${preferredPort}`;
  if (await isHealthy(existingBaseUrl)) {
    // A backend (likely started manually for development) is already serving this port.
    logLine(`Found an already-running backend at ${existingBaseUrl}.`);
    return { baseUrl: existingBaseUrl, alreadyRunning: true };
  }

  const port = await findAvailablePort(preferredPort, host);
  const baseUrl = `http://${host}:${port}`;

  if (isPackaged) {
    const exeName = process.platform === 'win32' ? 'riva-backend.exe' : 'riva-backend';
    const exePath = path.join(process.resourcesPath, 'backend', exeName);
    if (!existsSync(exePath)) {
      const message = `Backend executable not found at ${exePath}.`;
      logLine(`[error] ${message}`);
      throw new Error(`${message} See ${logPath} for details.`);
    }
    logLine(`Launching packaged backend: ${exePath} (host=${host}, port=${port})`);
    backendProcess = spawn(exePath, [], {
      env: { ...process.env, BACKEND_HOST: host, BACKEND_PORT: String(port) },
      stdio: 'pipe',
    });
  } else {
    const backendDir = path.join(appRoot, '..', 'backend');
    const pythonBin = process.platform === 'win32' ? 'python' : 'python3';
    logLine(`Launching dev backend: ${pythonBin} run.py (cwd=${backendDir}, host=${host}, port=${port})`);
    backendProcess = spawn(pythonBin, ['run.py'], {
      cwd: backendDir,
      env: { ...process.env, BACKEND_HOST: host, BACKEND_PORT: String(port) },
      stdio: 'pipe',
    });
  }

  interface ExitInfo {
    code: number | null;
    signal: NodeJS.Signals | null;
  }
  const launchState: { spawnError: Error | null; exitInfo: ExitInfo | null } = {
    spawnError: null,
    exitInfo: null,
  };

  backendProcess.stdout?.on('data', (data) => logLine(`[backend] ${data.toString().trimEnd()}`));
  backendProcess.stderr?.on('data', (data) => logLine(`[backend] ${data.toString().trimEnd()}`));
  backendProcess.on('error', (err) => {
    launchState.spawnError = err;
    logLine(`[error] Failed to launch the backend process: ${err.message}`);
  });
  backendProcess.on('exit', (code, signal) => {
    launchState.exitInfo = { code, signal };
    logLine(`[backend] process exited (code=${code}, signal=${signal})`);
    backendProcess = null;
  });

  await new Promise((resolve) => setTimeout(resolve, SPAWN_SETTLE_MS));
  if (launchState.spawnError) {
    throw new Error(
      `RIVA's backend process could not be launched (${launchState.spawnError.message}). See ${logPath} for details.`
    );
  }

  const healthy = await waitForHealth(baseUrl, HEALTH_TIMEOUT_MS, () => launchState.exitInfo !== null);
  if (!healthy) {
    const finalExitInfo = launchState.exitInfo;
    if (finalExitInfo) {
      throw new Error(
        `The RIVA backend process exited unexpectedly (code ${finalExitInfo.code}) before it became ready. See ${logPath} for details.`
      );
    }
    throw new Error(
      `The RIVA backend did not respond in time. It may still be starting on a slow first launch, or antivirus software may be blocking it. See ${logPath} for details.`
    );
  }

  logLine('Backend is healthy.');
  return { baseUrl, alreadyRunning: false };
}

export function stopBackend(): void {
  if (backendProcess && !backendProcess.killed) {
    backendProcess.kill();
    backendProcess = null;
  }
}
