#!/usr/bin/env bash
# RIVA AI - macOS/Linux setup script (development convenience; production target is Windows).
# Run from the repository root: bash scripts/setup.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "== RIVA AI setup =="

echo "Creating Python virtual environment..."
cd "$REPO_ROOT/backend"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "Installing Playwright's Chromium browser..."
playwright install chromium || echo "Playwright browser install failed or was blocked — browser_read_page will report this gracefully at runtime."
cd "$REPO_ROOT"

echo "Installing desktop (Electron/React) dependencies..."
cd "$REPO_ROOT/desktop"
npm install
cd "$REPO_ROOT"

if [ ! -f "$REPO_ROOT/.env" ]; then
  cp "$REPO_ROOT/.env.example" "$REPO_ROOT/.env"
  echo "Created .env from .env.example — add your LLM and voice API keys before running RIVA."
else
  echo ".env already exists — leaving it unchanged."
fi

echo "Setup complete. Run scripts/dev.sh to start RIVA in development mode."
