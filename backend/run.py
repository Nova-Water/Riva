"""Development/production entrypoint: runs the FastAPI app with uvicorn.

Also used as the PyInstaller entrypoint when the backend is packaged for
the Windows installer (see build_backend.py).
"""
from __future__ import annotations

import uvicorn

from app.config import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
