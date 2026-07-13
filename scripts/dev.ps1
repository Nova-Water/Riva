# RIVA AI - Windows development launcher
# Starts the FastAPI backend and the Electron/Vite frontend together.
# Run from the repository root: powershell -ExecutionPolicy Bypass -File scripts/dev.ps1

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot

Write-Host "Starting RIVA backend..." -ForegroundColor Cyan
$backend = Start-Process -PassThru -NoNewWindow powershell -ArgumentList `
    "-NoExit", "-Command", "cd '$RepoRoot/backend'; .venv/Scripts/Activate.ps1; python run.py"

Start-Sleep -Seconds 2

Write-Host "Starting RIVA desktop app (Vite + Electron)..." -ForegroundColor Cyan
Push-Location "$RepoRoot/desktop"
try {
    npm run dev
} finally {
    Pop-Location
    if ($backend -and -not $backend.HasExited) {
        Stop-Process -Id $backend.Id -Force
    }
}
