"""OpenAI-compatible chat completion provider.

Works with the real OpenAI API and any self-hosted or third-party service
that implements the same `/chat/completions` contract (vLLM, LM Studio,
Azure-compatible gateways, OpenRouter, etc.). If LLM_BASE_URL is left
empty we fall back to the official OpenAI endpoint.
"""
from __future__ import annotations

import httpx

from app.providers.llm.base import LLMMessage, LLMProvider, LLMProviderError, LLMResponse

DEFAULT_BASE_URL = "https://api.openai.com/v1"


class OpenAICompatibleProvider(LLMProvider):
    name = "openai_compatible"

    def __init__(self, api_key: str, base_url: str, model: str):
        self._api_key = api_key
        self._base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self._model = model

    def is_configured(self) -> bool:
        return bool(self._api_key and self._model)

    async def complete(self, messages: list[LLMMessage], *, timeout_seconds: float = 30.0) -> LLMResponse:
        if not self.is_configured():
            raise LLMProviderError(
                "The LLM provider is not configured. Add LLM_API_KEY and LLM_MODEL to your .env file."
            )

        payload = {
            "model": self._model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": 0.4,
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=timeout_seconds) as client:
                resp = await client.post(
                    f"{self._base_url}/chat/completions", json=payload, headers=headers
                )
        except httpx.TimeoutException as exc:
            raise LLMProviderError("The LLM provider timed out. Please try again.") from exc
        except httpx.ConnectError as exc:
            raise LLMProviderError(
                "Could not reach the LLM provider. Check your internet connection or LLM_BASE_URL."
            ) from exc

        if resp.status_code == 401:
            raise LLMProviderError("The LLM API key was rejected. Check LLM_API_KEY in your .env file.")
        if resp.status_code == 404:
            raise LLMProviderError(
                "The LLM model or endpoint was not found. Check LLM_MODEL and LLM_BASE_URL."
            )
        if resp.status_code >= 400:
            raise LLMProviderError(f"The LLM provider returned an error (status {resp.status_code}).")

        try:
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, ValueError) as exc:
            raise LLMProviderError("The LLM provider returned an unexpected response format.") from exc

        return LLMResponse(raw_text=content, model=self._model)
