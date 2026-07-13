"""Local speech-to-text using Faster-Whisper. No API key required.

The model is loaded lazily on first use so backend startup is fast and a
missing/failed model download does not crash the whole application.
"""
from __future__ import annotations

from app.logging_config import get_logger
from app.providers.stt.base import STTProvider, STTProviderError, TranscriptionResult

logger = get_logger("stt.faster_whisper")


class FasterWhisperProvider(STTProvider):
    name = "faster_whisper"

    def __init__(self, model_size: str, device: str, compute_type: str):
        self._model_size = model_size
        self._device = device
        self._compute_type = compute_type
        self._model = None
        self._load_error: str | None = None

    def _ensure_model(self):
        if self._model is not None or self._load_error is not None:
            return
        try:
            from faster_whisper import WhisperModel  # imported lazily; heavy dependency

            self._model = WhisperModel(
                self._model_size, device=self._device, compute_type=self._compute_type
            )
            logger.info("Faster-Whisper model '%s' loaded on %s", self._model_size, self._device)
        except Exception as exc:  # noqa: BLE001 - any load failure should degrade gracefully
            self._load_error = str(exc)
            logger.warning("Faster-Whisper model failed to load: %s", exc)

    def is_available(self) -> bool:
        self._ensure_model()
        return self._model is not None

    def transcribe(self, audio_path: str) -> TranscriptionResult:
        self._ensure_model()
        if self._model is None:
            raise STTProviderError(
                "The local speech-to-text model is unavailable. "
                "It may still be downloading, or model files are missing. "
                "You can continue using RIVA in text mode."
            )
        try:
            segments, info = self._model.transcribe(audio_path, beam_size=5)
            text = " ".join(segment.text.strip() for segment in segments).strip()
        except Exception as exc:  # noqa: BLE001
            raise STTProviderError(f"Transcription failed: {exc}") from exc

        return TranscriptionResult(
            text=text,
            language=getattr(info, "language", None),
            duration_seconds=getattr(info, "duration", None),
        )
