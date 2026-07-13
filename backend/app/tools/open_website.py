"""open_website: open a validated http/https URL in the default browser (green permission)."""
from __future__ import annotations

import subprocess
import sys
import webbrowser

from pydantic import BaseModel, Field

from app.security.url_validation import UrlSecurityError, validate_url
from app.tools.registry import ToolDefinition, registry
from app.tools.schemas import PermissionLevel, ToolContext, ToolError, ToolResult


class OpenWebsiteInput(BaseModel):
    url: str = Field(..., description="A full http:// or https:// URL to open.")


async def handle_open_website(args: OpenWebsiteInput, ctx: ToolContext) -> ToolResult:
    try:
        safe_url = validate_url(args.url)
    except UrlSecurityError as exc:
        raise ToolError(str(exc)) from exc

    try:
        if sys.platform == "win32":
            subprocess.Popen(["cmd", "/c", "start", "", safe_url], shell=False)
        else:
            webbrowser.open(safe_url)
    except Exception as exc:  # noqa: BLE001
        raise ToolError(f"Could not open the website: {exc}") from exc

    return ToolResult(success=True, data={"url": safe_url}, message=f"Opened {safe_url} in your browser.")


registry.register(
    ToolDefinition(
        name="open_website",
        description="Open a website in the default browser. Only http/https links are permitted.",
        input_model=OpenWebsiteInput,
        permission_level=PermissionLevel.GREEN,
        handler=handle_open_website,
        confirmation_template="Open {url}?",
    )
)
