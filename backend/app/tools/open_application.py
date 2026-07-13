"""open_application: launch an allow-listed application only (green permission)."""
from __future__ import annotations

import subprocess

from pydantic import BaseModel, Field

from app.tools.registry import ToolDefinition, registry
from app.tools.schemas import PermissionLevel, ToolContext, ToolError, ToolResult


class OpenApplicationInput(BaseModel):
    application: str = Field(
        ..., description="Application alias, e.g. 'notepad', 'browser', 'calculator', 'MYSKA Pay', 'NovaCore'."
    )


async def handle_open_application(args: OpenApplicationInput, ctx: ToolContext) -> ToolResult:
    app = ctx.app_allowlist.resolve(args.application)
    if app is None:
        raise ToolError(
            f"'{args.application}' is not in the approved application list. "
            "Ask an administrator to add it in settings."
        )

    command = ctx.app_allowlist.launch_command(args.application)
    if not command:
        raise ToolError(f"No launch command is configured for '{args.application}'.")

    try:
        subprocess.Popen(command, shell=False)
    except FileNotFoundError as exc:
        raise ToolError(f"'{app.display_name}' could not be launched: not found on this system.") from exc
    except Exception as exc:  # noqa: BLE001
        raise ToolError(f"'{app.display_name}' could not be launched: {exc}") from exc

    return ToolResult(success=True, data={"application": app.display_name}, message=f"Opened {app.display_name}.")


registry.register(
    ToolDefinition(
        name="open_application",
        description=(
            "Open an approved application by alias (e.g. notepad, browser, calculator, "
            "file explorer, MYSKA Pay, NovaCore). Only pre-approved applications can be launched."
        ),
        input_model=OpenApplicationInput,
        permission_level=PermissionLevel.GREEN,
        handler=handle_open_application,
        confirmation_template="Open {application}?",
    )
)
