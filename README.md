# RIVA AI

RIVA AI is Nova Tech Ltd's Windows desktop AI assistant — a Samoan-owned
technology company providing IT support, computer consultation and repair,
CCTV security systems, networking, websites, software systems, cybersecurity
and business technology services.

RIVA accepts push-to-talk voice commands, transcribes them locally, reasons
about what you're asking for, safely runs approved tools, speaks its
responses, and remembers your conversations — all through a professional,
animated desktop interface.

## Main Features

- **Push-to-talk voice input** with local, offline transcription (Faster-Whisper — no STT API key required).
- **Modular LLM provider system** (OpenAI-compatible by default; pluggable).
- **Modular text-to-speech** (ElevenLabs-compatible by default) with automatic, non-fatal fallback to text-only mode.
- **Structured tool-calling agent** — the LLM never runs a raw command; every action is validated against a Pydantic schema and a permission level (green / amber / red).
- **Confirmation workflow** for sensitive actions, with a clear approve/reject modal that expires automatically.
- **MVP tools**: PC status, open approved applications/websites, search & read approved files, create documents, search the local knowledgebase, draft emails (never sent), generate social posts, read web pages with Playwright.
- **Read-only business integrations**: MYSKA Pay (payroll) and NovaCore (sales/inventory), both clearly reporting "not connected" until configured — no fabricated data.
- **Persistent memory**: conversations, tool calls, confirmations, and email drafts are stored locally in SQLite; long threads are summarised instead of replaying full history to the LLM.
- **Local full-text knowledgebase search** (SQLite FTS5) over `knowledge/nova-tech`, `knowledge/myska-pay`, `knowledge/novacore`, `knowledge/procedures`.
- **Animated avatar** with idle / listening / thinking / speaking / error / offline states, built as a placeholder ready to be swapped for a final asset (PNG, WebP, video, Lottie, or GLB).
- **Windows installer** via Electron Builder (NSIS), with desktop + Start Menu shortcuts and app-data preserved on uninstall by default.

## Architecture

```
riva-ai/
├── desktop/        Electron + React + TypeScript + Vite frontend
│   ├── electron/    Main process, preload bridge, backend process manager
│   └── src/         React app: components, hooks, services, stores, types
├── backend/        Python 3.11+ FastAPI backend
│   └── app/
│       ├── agent/       System prompt + structured action parsing + orchestration loop
│       ├── providers/   Modular LLM / STT / TTS provider interfaces + implementations
│       ├── tools/       Tool registry, permission levels, and every MVP tool
│       ├── security/    Path validation, app/URL allowlists, confirmation store
│       ├── memory/      Recent-window context + long-thread summarisation
│       └── database/    SQLAlchemy models + SQLite (+ FTS5 knowledgebase index)
├── knowledge/       Approved company documents RIVA can search
├── scripts/         Setup/dev launcher scripts (Windows + macOS/Linux)
└── docs/            Security, tool-authoring, and integration guides
```

The Electron frontend and Python backend are fully separate processes that
talk over a local-only HTTP API (`http://127.0.0.1:8765` by default). No API
key is ever sent to or stored in the renderer — every AI/voice call goes
through the backend.

## Development Setup

See **[SETUP_WINDOWS.md](SETUP_WINDOWS.md)** for full Windows instructions.
Summary:

1. Install Python 3.11+ and Node.js 20+.
2. `cd backend && python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt`
3. `playwright install chromium`
4. `cd ../desktop && npm install`
5. Copy `.env.example` to `.env` in the repo root and fill in your LLM/voice keys.
6. From the repo root: `powershell -ExecutionPolicy Bypass -File scripts/dev.ps1` (or `bash scripts/dev.sh` on macOS/Linux).

## How to Run

- **Development**: `scripts/dev.ps1` (Windows) or `scripts/dev.sh` (macOS/Linux) — starts the FastAPI backend and the Electron/Vite app together.
- **Backend only**: `cd backend && python run.py`
- **Frontend only** (backend must already be running): `cd desktop && npm run dev`

## How to Build

```bash
cd desktop
npm run build          # Type-check, build the renderer, compile Electron main/preload
npm run package:win     # Full Windows installer (also packages the Python backend via PyInstaller)
```

To package the backend into a standalone executable on its own:

```bash
cd backend
python build_backend.py   # Produces backend/dist/riva-backend(.exe) via PyInstaller
```

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Startup screen never finishes | Backend didn't start | Check `backend` process output; confirm Python deps installed |
| "LLM Not configured" in the status bar | Missing `LLM_API_KEY` / `LLM_MODEL` | Edit `.env` in the repo root |
| "Voice Text-only mode" | Missing `VOICE_API_KEY` / `VOICE_ID`, or the voice API is down | RIVA keeps working in text mode by design |
| Microphone button shows an error | No mic found, or permission denied | Check OS microphone permissions for RIVA AI |
| `browser_read_page` fails with "Playwright... not installed" | Chromium wasn't downloaded | Run `playwright install chromium` inside the backend venv |
| Knowledgebase search returns nothing | Index is empty | Open Settings → Knowledgebase → Reindex now |

## Current Limitations

This is a functional MVP, not the finished business operating assistant. By design, it does **not** include: automatic payments, automatic email sending, full mouse/keyboard control, unrestricted PowerShell, file deletion, payroll processing, credential management, remote access to other machines, an always-listening wake word, or facial recognition/surveillance features. MYSKA Pay and NovaCore integrations are read-only placeholders until their real API contracts are connected (see `docs/INTEGRATIONS.md`).
