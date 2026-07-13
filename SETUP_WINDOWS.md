# RIVA AI — Windows Setup Guide

Step-by-step instructions to run RIVA AI on Windows 10/11 for development.

## 1. Install Node.js

Download and install **Node.js 20 LTS or later** from https://nodejs.org.
Confirm it installed correctly:

```powershell
node --version
npm --version
```

## 2. Install Python

Download and install **Python 3.11 or later** from https://python.org.
During installation, check **"Add python.exe to PATH"**. Confirm:

```powershell
python --version
```

## 3. Clone or Copy the Project

Place the `riva-ai` folder somewhere without unusual permission restrictions,
e.g. `C:\Users\<you>\Projects\riva-ai`. Paths containing spaces are
supported, but a simple path is easiest for troubleshooting.

## 4. Create the Backend Virtual Environment

```powershell
cd riva-ai\backend
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks the activation script, run once as Administrator:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## 5. Install Backend Requirements

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

## 6. Install Frontend Dependencies

```powershell
cd ..\desktop
npm install
```

## 7. Install the Playwright Browser

Back in the backend virtual environment:

```powershell
cd ..\backend
.venv\Scripts\Activate.ps1
playwright install chromium
```

This enables the `browser_read_page` tool. If skipped, RIVA still runs
normally — that one tool will report that the browser isn't installed.

## 8. Download the Faster-Whisper Model

No manual download is required — the first time you use voice input, RIVA
automatically downloads the `base` Faster-Whisper model (set by
`STT_MODEL_SIZE` in `.env`) and caches it locally. This requires an internet
connection the first time only. If the download fails, RIVA continues to
work in text-only mode and shows a clear warning.

## 9. Copy `.env.example` to `.env`

From the repository root (not inside `backend/` or `desktop/`):

```powershell
copy .env.example .env
```

**Never commit `.env`** — it's already in `.gitignore`.

## 10. Add the LLM API Key

Open `.env` in a text editor and set:

```env
LLM_PROVIDER=openai_compatible
LLM_API_KEY=sk-...your-key...
LLM_BASE_URL=
LLM_MODEL=gpt-4o-mini
```

Leave `LLM_BASE_URL` empty to use the provider's default endpoint, or point
it at a self-hosted / third-party OpenAI-compatible endpoint.

## 11. Add the Voice API Key and Voice ID

```env
TTS_PROVIDER=elevenlabs
VOICE_API_KEY=...your-elevenlabs-key...
VOICE_ID=...your-voice-id...
VOICE_MODEL_ID=
VOICE_BASE_URL=
```

If left blank, RIVA runs in text-only mode with a clear notice in the status
bar — it will not crash.

## 12. Start Development Mode

From the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\dev.ps1
```

This starts the FastAPI backend and then launches the Electron app, which
waits for `/health` before showing the full interface.

## 13. Build the Installer

```powershell
cd backend
python build_backend.py

cd ..\desktop
npm run package:win
```

The finished installer appears in `desktop\release\`. It supports Windows 10
and 11, offers desktop and Start Menu shortcuts, and preserves your local
RIVA data (`%APPDATA%\RIVA AI`) on uninstall unless you choose to remove it.

## Troubleshooting

- **`python` not found**: reinstall Python and ensure "Add to PATH" was checked, or use `py -3.11` instead of `python`.
- **PowerShell script execution blocked**: run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, as shown in step 4.
- **Backend fails to start**: activate the virtual environment and run `python run.py` directly inside `backend/` to see the full error.
- **Microphone doesn't work**: check Windows Settings → Privacy & Security → Microphone, and make sure RIVA AI (or your terminal, in dev mode) is allowed access.
