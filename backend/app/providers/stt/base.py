"""Speech-to-text provider interface."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


class STTProviderError(Exception):
    pass


@dataclass
class TranscriptionResult:
    text: str
    language: str | None = None
    duration_seconds: float | None = None


class STTProvider(ABC):
    name: str = "base"

    @abstractmethod
    def transcribe(self, audio_path: str) -> TranscriptionResult:
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        raise NotImplementedError
