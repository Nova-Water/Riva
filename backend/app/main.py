"""RIVA AI backend entrypoint (FastAPI application).

Local-only by design: CORS is restricted to the Electron app's origins and
the server binds to 127.0.0.1 by default. This backend is never intended
to be exposed to the public network.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database.db import init_database
from app.logging_config import configure_logging, get_logger

# Importing app.tools registers every MVP tool into the shared registry.
import app.tools  # noqa: F401

from app.api import (
    routes_assistant,
    routes_conversations,
    routes_drafts,
    routes_health,
    routes_knowledge,
    routes_speech,
    routes_tools,
)
from app.state import get_state
from app.tools.knowledgebase import reindex_knowledge_base

logger = get_logger("main")

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "app://.",
    "file://",
]


@asynccontextmanager
async def _lifespan(app: FastAPI):
    settings = get_settings()
    logger.info("Starting %s (%s)", settings.app_name, settings.app_env)
    init_database()
    state = get_state()
    if not state.llm_provider.is_configured():
        logger.warning(
            "LLM provider is not configured — RIVA will run in limited mode until "
            "LLM_API_KEY and LLM_MODEL are set."
        )
    if not state.tts_provider.is_configured():
        logger.warning(
            "Voice provider is not configured — RIVA will run in text-only mode until "
            "VOICE_API_KEY and VOICE_ID are set."
        )
    try:
        count = reindex_knowledge_base(settings.knowledge_directory)
        logger.info("Knowledgebase indexed: %s documents", count)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Knowledgebase indexing failed at startup: %s", exc)
    logger.info("RIVA backend ready on %s:%s", settings.backend_host, settings.backend_port)

    yield


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()

    app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=_lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(routes_health.router)
    app.include_router(routes_assistant.router)
    app.include_router(routes_speech.router)
    app.include_router(routes_conversations.router)
    app.include_router(routes_drafts.router)
    app.include_router(routes_knowledge.router)
    app.include_router(routes_tools.router)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        # Never leak internal details (which could include provider errors containing
        # fragments of request data) to the client; log the full detail locally instead.
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(status_code=500, content={"error": "internal_error", "detail": "An unexpected error occurred."})

    return app


app = create_app()
