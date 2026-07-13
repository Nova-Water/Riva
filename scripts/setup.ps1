# RIVA AI - Windows setup script
# Installs backend (Python) and desktop (Node) dependencies and prepares .env.
# Run from the repository root: powershell -ExecutionPolicy Bypass -File scripts/setup.ps1

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot

Write-Host "== RIVA AI setup ==" -ForegroundColor Cyan

# --- Backend ---
Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
Push-Location "$RepoRoot/backend"
python -m venv .venv
& ".venv/Scripts/Activate.ps1"
pip install --upgrade pip
pip install -r requirements.txt
Write-Host "Installing Playwright's Chromium browser..." -ForegroundColor Yellow
playwright install chromium
Pop-Location

# --- Frontend ---
Write-Host "Installing desktop (Electron/React) dependencies..." -ForegroundColor Yellow
Push-Location "$RepoRoot/desktop"
npm install
Pop-Location

# --- Environment file ---
$envPath = Join-Path $RepoRoot ".env"
$envExamplePath = Join-Path $RepoRoot ".env.example"
if (-not (Test-Path $envPath)) {
    Copy-Item $envExamplePath $envPath
    Write-Host "Created .env from .env.example — add your LLM and voice API keys before running RIVA." -ForegroundColor Green
} else {
    Write-Host ".env already exists — leaving it unchanged." -ForegroundColor Green
}

Write-Host "Setup complete. Run scripts/dev.ps1 to start RIVA in development mode." -ForegroundColor Cyan
