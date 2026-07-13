"""create_document: create a .txt or .md file in the approved output folder (amber permission)."""
from __future__ import annotations

from pydantic import BaseModel, Field

from app.security.path_validation import PathSecurityError, validate_new_file_path
from app.tools.registry import ToolDefinition, registry
from app.tools.schemas import PermissionLevel, ToolContext, ToolError, ToolResult

ALLOWED_EXTENSIONS = [".txt", ".md"]


class CreateDocumentInput(BaseModel):
    filename: str = Field(..., description="Filename ending in .txt or .md, e.g. 'quotation-notes.md'.")
    content: str = Field(..., description="The text content to write into the document.")
    overwrite: bool = Field(default=False, description="Must be true to overwrite an existing file.")


async def handle_create_document(args: CreateDocumentInput, ctx: ToolContext) -> ToolResult:
    output_dir = ctx.settings.documents_output_directory
    target_raw = str(output_dir / args.filename)

    try:
        resolved = validate_new_file_path(target_raw, [output_dir], ALLOWED_EXTENSIONS)
    except PathSecurityError as exc:
        raise ToolError(str(exc)) from exc

    if resolved.exists() and not args.overwrite:
        raise ToolError(
            f"'{resolved.name}' already exists. Ask again with overwrite confirmed to replace it."
        )

    resolved.parent.mkdir(parents=True, exist_ok=True)
    try:
        resolved.write_text(args.content, encoding="utf-8")
    except OSError as exc:
        raise ToolError(f"The document could not be created: {exc}") from exc

    return ToolResult(
        success=True,
        data={"file_path": str(resolved)},
        message=f"Created document '{resolved.name}'.",
    )


registry.register(
    ToolDefinition(
        name="create_document",
        description="Create a .txt or .md document in the approved output folder. Requires confirmation.",
        input_model=CreateDocumentInput,
        permission_level=PermissionLevel.AMBER,
        handler=handle_create_document,
        confirmation_template="Create document '{filename}' in the approved output folder?",
    )
)
