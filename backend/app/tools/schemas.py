"""Shared tool data types: permission levels, execution context, and results."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from app.config import Settings
from app.security.app_allowlist import ApplicationAllowlist


class PermissionLevel(str, Enum):
    GREEN = "green"
    AMBER = "amber"
    RED = "red"


@dataclass
class ToolContext:
    """Everything a tool handler needs, injected by the agent — never by the LLM."""

    settings: Settings
    conversation_id: str
    app_allowlist: ApplicationAllowlist


@dataclass
class ToolResult:
    success: bool
    data: Any = None
    message: str = ""
    error: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {"success": self.success, "data": self.data, "message": self.message, "error": self.error}


class ToolError(Exception):
    """Raised by a tool handler for an expected, user-facing failure."""
