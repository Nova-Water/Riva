"""Factory + process-wide singleton for the STT provider (model load is expensive)."""
from __future__ import annotations

from app.config import Settings
from app.providers.stt.base import STTProvider
from app.providers.stt.faster_whisper_provider import FasterWhisperProvider

_instance: STTProvider | None = None


def create_stt_provider(settings: Settings) -> STTProvider:
    global _instance
    if _instance is None:
        _instance = FasterWhisperProvider(
            model_size=settings.stt_model_size,
            device=settings.stt_device,
            compute_type=settings.stt_compute_type,
        )
    return _instance
