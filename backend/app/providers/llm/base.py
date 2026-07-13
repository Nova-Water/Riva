"""LLM provider interface. Every LLM backend must implement this contract."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


class LLMProviderError(Exception):
    """Raised for any recoverable LLM provider failure (timeout, auth, bad response)."""


@dataclass
class LLMMessage:
    role: str  # "system" | "user" | "assistant"
    content: str


@dataclass
class LLMResponse:
    raw_text: str
    model: str


class LLMProvider(ABC):
    """Abstract base for chat-completion style LLM providers."""

    name: str = "base"

    @abstractmethod
    async def complete(self, messages: list[LLMMessage], *, timeout_seconds: float = 30.0) -> LLMResponse:
        """Send a chat completion request and return the raw text response."""
        raise NotImplementedError

    @abstractmethod
    def is_configured(self) -> bool:
        raise NotImplementedError
