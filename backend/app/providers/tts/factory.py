"""Factory that selects the configured TTS provider implementation."""
from __future__ import annotations

from app.config import Settings
from app.providers.tts.base import TTSProvider
from app.providers.tts.elevenlabs_provider import ElevenLabsProvider

_PROVIDERS = {
    "elevenlabs": ElevenLabsProvider,
}


def create_tts_provider(settings: Settings) -> TTSProvider:
    provider_cls = _PROVIDERS.get(settings.tts_provider, ElevenLabsProvider)
    return provider_cls(
        api_key=settings.voice_api_key,
        voice_id=settings.voice_id,
        model_id=settings.voice_model_id,
        base_url=settings.voice_base_url,
    )
