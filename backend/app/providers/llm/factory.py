"""Factory that selects the configured LLM provider implementation."""
from __future__ import annotations

from app.config import Settings
from app.providers.llm.base import LLMProvider
from app.providers.llm.openai_compatible import OpenAICompatibleProvider

_PROVIDERS = {
    "openai_compatible": OpenAICompatibleProvider,
}


def create_llm_provider(settings: Settings) -> LLMProvider:
    provider_cls = _PROVIDERS.get(settings.llm_provider, OpenAICompatibleProvider)
    return provider_cls(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        model=settings.llm_model,
    )
