#!/usr/bin/env bash
# RIVA AI - macOS/Linux development launcher (development convenience; production target is Windows).
# Starts the FastAPI backend and the Electron/Vite frontend together.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cleanup() {
  if [ -n "${BACKEND_PID:-}" ]; then
    kill "$BACKEND_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

echo "Starting RIVA backend..."
cd "$REPO_ROOT/backend"
source .venv/bin/activate
python run.py &
BACKEND_PID=$!
cd "$REPO_ROOT"

sleep 2

echo "Starting RIVA desktop app (Vite + Electron)..."
cd "$REPO_ROOT/desktop"
npm run dev
