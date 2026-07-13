"""Central application configuration loaded from environment variables.

All settings live here so the rest of the backend never reads os.environ
directly. This keeps credential handling auditable in one place.
"""
from __future__ import annotations

import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from pydantic import BaseModel, Field


def _project_root() -> Path:
    # backend/app/config.py -> backend/ -> project root
    return Path(__file__).resolve().parents[2]


def _load_env() -> None:
    env_path = _project_root() / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=False)
    else:
        # Fall back to whatever is already in the process environment.
        # A missing .env is a valid (if degraded) state, not a fatal error.
        pass


_load_env()


def _default_data_directory() -> Path:
    """Windows-appropriate application data directory, with sane fallbacks."""
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        return Path(base) / "RIVA AI"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "RIVA AI"
    xdg = os.environ.get("XDG_DATA_HOME")
    base = Path(xdg) if xdg else Path.home() / ".local" / "share"
    return base / "riva-ai"


def _split_paths(value: str) -> List[str]:
    return [p.strip() for p in value.split(os.pathsep) if p.strip()] if value else []


def _split_list(value: str) -> List[str]:
    return [p.strip() for p in value.split(",") if p.strip()] if value else []


class Settings(BaseModel):
    app_name: str = Field(default="RIVA AI")
    app_env: str = Field(default="development")
    backend_host: str = Field(default="127.0.0.1")
    backend_port: int = Field(default=8765)

    llm_provider: str = Field(default="openai_compatible")
    llm_api_key: str = Field(default="")
    llm_base_url: str = Field(default="")
    llm_model: str = Field(default="")

    tts_provider: str = Field(default="elevenlabs")
    voice_api_key: str = Field(default="")
    voice_id: str = Field(default="")
    voice_model_id: str = Field(default="")
    voice_base_url: str = Field(default="")

    stt_model_size: str = Field(default="base")
    stt_device: str = Field(default="cpu")
    stt_compute_type: str = Field(default="int8")

    data_directory: Path
    allowed_file_roots: List[str] = Field(default_factory=list)
    allowed_applications: List[str] = Field(default_factory=list)

    myska_api_base_url: str = Field(default="")
    myska_api_key: str = Field(default="")
    novacore_api_base_url: str = Field(default="")
    novacore_api_key: str = Field(default="")

    project_root: Path

    @property
    def database_path(self) -> Path:
        return self.data_directory / "riva.db"

    @property
    def logs_directory(self) -> Path:
        return self.data_directory / "logs"

    @property
    def documents_output_directory(self) -> Path:
        return self.data_directory / "documents"

    @property
    def knowledge_directory(self) -> Path:
        return self.project_root / "knowledge"

    @property
    def effective_allowed_file_roots(self) -> List[Path]:
        roots = [Path(p) for p in self.allowed_file_roots]
        roots.append(self.documents_output_directory)
        roots.append(self.knowledge_directory)
        return roots

    def llm_configured(self) -> bool:
        return bool(self.llm_api_key and self.llm_model)

    def voice_configured(self) -> bool:
        return bool(self.voice_api_key and self.voice_id)

    def myska_configured(self) -> bool:
        return bool(self.myska_api_base_url and self.myska_api_key)

    def novacore_configured(self) -> bool:
        return bool(self.novacore_api_base_url and self.novacore_api_key)

    def masked(self, value: str, keep: int = 4) -> str:
        if not value:
            return ""
        if len(value) <= keep:
            return "*" * len(value)
        return value[:keep] + "*" * max(len(value) - keep, 4)


@lru_cache
def get_settings() -> Settings:
    root = _project_root()
    data_dir_env = os.environ.get("RIVA_DATA_DIRECTORY", "").strip()
    data_directory = Path(data_dir_env) if data_dir_env else _default_data_directory()

    settings = Settings(
        app_name=os.environ.get("APP_NAME", "RIVA AI"),
        app_env=os.environ.get("APP_ENV", "development"),
        backend_host=os.environ.get("BACKEND_HOST", "127.0.0.1"),
        backend_port=int(os.environ.get("BACKEND_PORT", "8765") or 8765),
        llm_provider=os.environ.get("LLM_PROVIDER", "openai_compatible"),
        llm_api_key=os.environ.get("LLM_API_KEY", ""),
        llm_base_url=os.environ.get("LLM_BASE_URL", ""),
        llm_model=os.environ.get("LLM_MODEL", ""),
        tts_provider=os.environ.get("TTS_PROVIDER", "elevenlabs"),
        voice_api_key=os.environ.get("VOICE_API_KEY", ""),
        voice_id=os.environ.get("VOICE_ID", ""),
        voice_model_id=os.environ.get("VOICE_MODEL_ID", ""),
        voice_base_url=os.environ.get("VOICE_BASE_URL", ""),
        stt_model_size=os.environ.get("STT_MODEL_SIZE", "base"),
        stt_device=os.environ.get("STT_DEVICE", "cpu"),
        stt_compute_type=os.environ.get("STT_COMPUTE_TYPE", "int8"),
        data_directory=data_directory,
        allowed_file_roots=_split_paths(os.environ.get("RIVA_ALLOWED_FILE_ROOTS", "")),
        allowed_applications=_split_list(os.environ.get("RIVA_ALLOWED_APPLICATIONS", "")),
        myska_api_base_url=os.environ.get("MYSKA_API_BASE_URL", ""),
        myska_api_key=os.environ.get("MYSKA_API_KEY", ""),
        novacore_api_base_url=os.environ.get("NOVACORE_API_BASE_URL", ""),
        novacore_api_key=os.environ.get("NOVACORE_API_KEY", ""),
        project_root=root,
    )

    settings.data_directory.mkdir(parents=True, exist_ok=True)
    settings.logs_directory.mkdir(parents=True, exist_ok=True)
    settings.documents_output_directory.mkdir(parents=True, exist_ok=True)
    return settings
