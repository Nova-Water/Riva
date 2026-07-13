"""Health, configuration status, and system status endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.models.api_models import (
    ConfigStatusResponse,
    HealthResponse,
    ProviderStatus,
    SystemStatusResponse,
)
from app.state import AppState, get_state

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health(state: AppState = Depends(get_state)) -> HealthResponse:
    return HealthResponse(app_name=state.settings.app_name, app_env=state.settings.app_env)


@router.get("/config/status", response_model=ConfigStatusResponse)
async def config_status(state: AppState = Depends(get_state)) -> ConfigStatusResponse:
    settings = state.settings
    return ConfigStatusResponse(
        llm=ProviderStatus(
            configured=state.llm_provider.is_configured(),
            provider=settings.llm_provider,
            detail=settings.llm_model if state.llm_provider.is_configured() else "Not configured",
        ),
        voice=ProviderStatus(
            configured=state.tts_provider.is_configured(),
            provider=settings.tts_provider,
            detail=settings.masked(settings.voice_id) if state.tts_provider.is_configured() else "Not configured",
        ),
        stt=ProviderStatus(
            configured=state.stt_provider.is_available(),
            provider="faster_whisper",
            detail=settings.stt_model_size,
        ),
        myska=ProviderStatus(
            configured=settings.myska_configured(),
            provider="myska_pay",
            detail="Connected" if settings.myska_configured() else "Not connected",
        ),
        novacore=ProviderStatus(
            configured=settings.novacore_configured(),
            provider="novacore",
            detail="Connected" if settings.novacore_configured() else "Not connected",
        ),
        allowed_file_roots=[str(p) for p in settings.effective_allowed_file_roots],
        allowed_applications=[app.display_name for app in state.app_allowlist.list_apps()],
    )


@router.get("/system/status", response_model=SystemStatusResponse)
async def system_status(state: AppState = Depends(get_state)) -> SystemStatusResponse:
    return SystemStatusResponse(
        backend_connected=True,
        llm_connected=state.llm_provider.is_configured(),
        voice_connected=state.tts_provider.is_configured(),
        stt_available=state.stt_provider.is_available(),
        active_task=None,
    )
