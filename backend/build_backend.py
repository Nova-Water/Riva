"""Package the FastAPI backend into a single Windows executable with PyInstaller.

Run from the backend/ directory:

    python build_backend.py

Output: backend/dist/riva-backend(.exe) — bundled by Electron Builder into
the final Windows installer (see desktop/electron-builder.yml extraResources).
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent


def main() -> int:
    entry = BACKEND_DIR / "run.py"
    dist_dir = BACKEND_DIR / "dist"
    build_dir = BACKEND_DIR / "build"

    for stale in (dist_dir, build_dir):
        if stale.exists():
            shutil.rmtree(stale)

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name",
        "riva-backend",
        "--onefile",
        "--noconfirm",
        "--console",
        "--collect-all",
        "faster_whisper",
        "--hidden-import",
        "uvicorn.logging",
        "--hidden-import",
        "uvicorn.loops.auto",
        "--hidden-import",
        "uvicorn.protocols.http.auto",
        str(entry),
    ]

    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd, cwd=str(BACKEND_DIR))
    if result.returncode != 0:
        print("PyInstaller build failed.")
        return result.returncode

    print(f"Backend executable built at: {dist_dir / 'riva-backend'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
