"""ElevenLabs-compatible text-to-speech provider.

If the voice API is unavailable or misconfigured, callers must catch
TTSProviderError and fall back to text-only mode — RIVA must never crash
because voice is down.
"""
from __future__ import annotations

import httpx

from app.providers.tts.base import SpeechResult, TTSProvider, TTSProviderError

DEFAULT_BASE_URL = "https://api.elevenlabs.io/v1"
DEFAULT_MODEL_ID = "eleven_multilingual_v2"


class ElevenLabsProvider(TTSProvider):
    name = "elevenlabs"

    def __init__(self, api_key: str, voice_id: str, model_id: str, base_url: str):
        self._api_key = api_key
        self._voice_id = voice_id
        self._model_id = model_id or DEFAULT_MODEL_ID
        self._base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")

    def is_configured(self) -> bool:
        return bool(self._api_key and self._voice_id)

    async def synthesize(self, text: str) -> SpeechResult:
        if not self.is_configured():
            raise TTSProviderError(
                "Voice is not configured. Add VOICE_API_KEY and VOICE_ID to your .env file."
            )
        if not text.strip():
            raise TTSProviderError("No text was provided to speak.")

        url = f"{self._base_url}/text-to-speech/{self._voice_id}"
        headers = {
            "xi-api-key": self._api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }
        payload = {
            "text": text,
            "model_id": self._model_id,
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
        except httpx.TimeoutException as exc:
            raise TTSProviderError("The voice provider timed out.") from exc
        except httpx.ConnectError as exc:
            raise TTSProviderError("Could not reach the voice provider.") from exc

        if resp.status_code == 401:
            raise TTSProviderError("The voice API key was rejected.")
        if resp.status_code == 404:
            raise TTSProviderError("The configured Voice ID was not found.")
        if resp.status_code >= 400:
            raise TTSProviderError(f"The voice provider returned an error (status {resp.status_code}).")

        return SpeechResult(audio_bytes=resp.content, content_type="audio/mpeg")
