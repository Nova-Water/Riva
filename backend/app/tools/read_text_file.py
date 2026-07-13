"""read_text_file: read an approved text file's contents (green permission)."""
from __future__ import annotations

from pydantic import BaseModel, Field

from app.security.path_validation import PathSecurityError, validate_path_in_roots
from app.tools.registry import ToolDefinition, registry
from app.tools.schemas import PermissionLevel, ToolContext, ToolError, ToolResult

MAX_FILE_SIZE_BYTES = 512 * 1024


class ReadTextFileInput(BaseModel):
    file_path: str = Field(..., description="Absolute or relative path to a file inside an approved folder.")


async def handle_read_text_file(args: ReadTextFileInput, ctx: ToolContext) -> ToolResult:
    roots = ctx.settings.effective_allowed_file_roots
    try:
        resolved = validate_path_in_roots(args.file_path, roots)
    except PathSecurityError as exc:
        raise ToolError(str(exc)) from exc

    if not resolved.exists():
        raise ToolError("The requested file does not exist.")
    if not resolved.is_file():
        raise ToolError("The requested path is not a file.")

    size = resolved.stat().st_size
    if size > MAX_FILE_SIZE_BYTES:
        raise ToolError(
            f"The file is too large to read ({size // 1024} KB). Maximum is {MAX_FILE_SIZE_BYTES // 1024} KB."
        )

    try:
        content = resolved.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise ToolError(f"The file could not be read: {exc}") from exc

    return ToolResult(
        success=True,
        data={"file_path": str(resolved), "content": content, "size_bytes": size},
        message=f"Read {resolved.name}.",
    )


registry.register(
    ToolDefinition(
        name="read_text_file",
        description="Read the contents of an approved text file. Enforces a maximum file size.",
        input_model=ReadTextFileInput,
        permission_level=PermissionLevel.GREEN,
        handler=handle_read_text_file,
    )
)
