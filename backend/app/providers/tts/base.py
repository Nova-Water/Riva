"""Text-to-speech provider interface."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


class TTSProviderError(Exception):
    pass


@dataclass
class SpeechResult:
    audio_bytes: bytes
    content_type: str = "audio/mpeg"


class TTSProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def synthesize(self, text: str) -> SpeechResult:
        raise NotImplementedError

    @abstractmethod
    def is_configured(self) -> bool:
        raise NotImplementedError
