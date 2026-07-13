"""search_files: search filenames and text contents inside approved folders (green permission)."""
from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from app.tools.registry import ToolDefinition, registry
from app.tools.schemas import PermissionLevel, ToolContext, ToolError, ToolResult

SEARCHABLE_EXTENSIONS = {".txt", ".md", ".json", ".csv", ".log", ".html", ".py", ".js", ".ts", ".tsx", ".php"}
MAX_RESULTS = 25
MAX_FILE_SCAN_BYTES = 2 * 1024 * 1024
EXCERPT_RADIUS = 80


class SearchFilesInput(BaseModel):
    query: str = Field(..., description="Search text: matched against filenames and file contents.")
    max_results: int = Field(default=15, ge=1, le=MAX_RESULTS)


def _excerpt(content: str, query: str) -> str:
    idx = content.lower().find(query.lower())
    if idx == -1:
        return content[: EXCERPT_RADIUS * 2].strip()
    start = max(0, idx - EXCERPT_RADIUS)
    end = min(len(content), idx + len(query) + EXCERPT_RADIUS)
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(content) else ""
    return f"{prefix}{content[start:end].strip()}{suffix}"


async def handle_search_files(args: SearchFilesInput, ctx: ToolContext) -> ToolResult:
    roots = ctx.settings.effective_allowed_file_roots
    if not roots:
        raise ToolError("No approved file folders are configured.")

    query_lower = args.query.strip().lower()
    if not query_lower:
        raise ToolError("Please provide a search term.")

    results = []
    for root in roots:
        root_path = Path(root)
        if not root_path.exists() or not root_path.is_dir():
            continue
        for path in root_path.rglob("*"):
            if len(results) >= args.max_results:
                break
            if not path.is_file() or path.suffix.lower() not in SEARCHABLE_EXTENSIONS:
                continue

            filename_match = query_lower in path.name.lower()
            excerpt = ""
            content_match = False
            try:
                if path.stat().st_size <= MAX_FILE_SCAN_BYTES:
                    text = path.read_text(encoding="utf-8", errors="ignore")
                    if query_lower in text.lower():
                        content_match = True
                        excerpt = _excerpt(text, args.query)
            except OSError:
                continue

            if filename_match or content_match:
                results.append(
                    {
                        "file_path": str(path),
                        "filename": path.name,
                        "excerpt": excerpt or "(matched filename)",
                    }
                )

    return ToolResult(
        success=True,
        data={"results": results, "count": len(results)},
        message=f"Found {len(results)} matching file(s).",
    )


registry.register(
    ToolDefinition(
        name="search_files",
        description=(
            "Search filenames and contents of supported document types inside approved folders only."
        ),
        input_model=SearchFilesInput,
        permission_level=PermissionLevel.GREEN,
        handler=handle_search_files,
    )
)
