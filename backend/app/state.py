"""Process-wide singletons: settings, providers, agent, and application allowlist.

Centralised here so API routes and the agent share the exact same
provider instances instead of re-reading configuration on every request.
"""
from __future__ import annotations

from app.agent.agent import RivaAgent
from app.config import Settings, get_settings
from app.providers.llm.factory import create_llm_provider
from app.providers.stt.factory import create_stt_provider
from app.providers.tts.factory import create_tts_provider
from app.security.app_allowlist import ApplicationAllowlist
from app.tools.registry import registry as tool_registry_instance


class AppState:
    def __init__(self) -> None:
        self.settings: Settings = get_settings()
        self.app_allowlist = ApplicationAllowlist(self.settings.allowed_applications)
        self.llm_provider = create_llm_provider(self.settings)
        self.tts_provider = create_tts_provider(self.settings)
        self.stt_provider = create_stt_provider(self.settings)
        self.tool_registry = tool_registry_instance
        self.agent = RivaAgent(
            llm_provider=self.llm_provider,
            tool_registry=self.tool_registry,
            app_allowlist=self.app_allowlist,
            settings=self.settings,
        )


_state: AppState | None = None


def get_state() -> AppState:
    global _state
    if _state is None:
        _state = AppState()
    return _state
