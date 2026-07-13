# Adding a New RIVA Tool

Tools live in `backend/app/tools/`. Each tool is a self-contained module
with a Pydantic input model, an async handler, and a registration call.
Follow this pattern to add a new one safely.

## 1. Choose a permission level

- **Green** — read-only / non-destructive. No confirmation needed.
- **Amber** — creates or changes local state. Requires confirmation.
- **Red** — reserved for high-impact actions (sending, paying, deleting,
  credential/payroll changes). Requires confirmation and should be added
  deliberately, with the underlying action itself reviewed for safety —
  most red-level actions are still out of scope for RIVA entirely (see
  `docs/SECURITY.md`).

## 2. Create the tool module

```python
# backend/app/tools/my_new_tool.py
from pydantic import BaseModel, Field

from app.tools.registry import ToolDefinition, registry
from app.tools.schemas import PermissionLevel, ToolContext, ToolError, ToolResult


class MyNewToolInput(BaseModel):
    some_argument: str = Field(..., description="Explain exactly what this is for the LLM.")


async def handle_my_new_tool(args: MyNewToolInput, ctx: ToolContext) -> ToolResult:
    # Validate everything you touch — paths, apps, URLs — using the helpers
    # in app/security/*. Never trust ctx or args blindly.
    if not args.some_argument.strip():
        raise ToolError("some_argument cannot be empty.")

    # Do the work. Never fabricate a success result — only return
    # success=True if the action actually happened.
    return ToolResult(success=True, data={"result": "..."}, message="Did the thing.")


registry.register(
    ToolDefinition(
        name="my_new_tool",
        description="One clear sentence the LLM will read to decide when to call this.",
        input_model=MyNewToolInput,
        permission_level=PermissionLevel.GREEN,  # or AMBER / RED
        handler=handle_my_new_tool,
        confirmation_template="Do the thing with {some_argument}?",  # amber/red only
    )
)
```

## 3. Register the module

Add it to the import list in `backend/app/tools/__init__.py` so it runs at
startup:

```python
from app.tools import (
    ...,
    my_new_tool,
)
```

## 4. Enforce security at the boundary

If your tool touches the filesystem, applications, or URLs, reuse the
existing validators — don't write new ad-hoc checks:

- Filesystem: `app.security.path_validation.validate_path_in_roots` /
  `validate_new_file_path`
- Applications: `app.security.app_allowlist.ApplicationAllowlist`
- URLs: `app.security.url_validation.validate_url`

Never accept a raw file path, executable path, or shell command directly
from LLM-supplied arguments without validating it against an allowlist.

## 5. Write tests

Add a test file under `backend/tests/` following the existing pattern (see
`test_search_files.py` or `test_create_document.py`): construct a
`ToolContext`, call the handler directly, and assert both the happy path and
at least one rejected/invalid case.

## 6. Update the system prompt context (automatic)

You don't need to touch `backend/app/agent/system_prompt.py` — it builds the
tool list dynamically from the registry, including your new tool's
description and JSON schema.

## 7. Confirm the permission system still passes

Run `pytest backend/tests/test_permissions.py` and
`backend/tests/test_tool_registry.py` after adding a tool — they assert
every registered tool has a valid classification and that unknown/invalid
tool calls are still rejected.
