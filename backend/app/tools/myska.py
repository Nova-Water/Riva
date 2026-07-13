"""Read-only MYSKA Pay integration adapter tools (placeholders until the real API is connected).

MYSKA Pay is Nova Tech's payroll platform. In this MVP these tools are
read-only and will clearly report that the integration is not yet
connected if MYSKA_API_BASE_URL / MYSKA_API_KEY are not configured.
Never fabricate data when the API is unavailable.
"""
from __future__ import annotations

import httpx
from pydantic import BaseModel

from app.tools.registry import ToolDefinition, registry
from app.tools.schemas import PermissionLevel, ToolContext, ToolResult

NOT_CONNECTED_MESSAGE = (
    "The MYSKA Pay integration is not yet connected. Add MYSKA_API_BASE_URL and MYSKA_API_KEY "
    "to your .env file to enable this feature. See docs/INTEGRATIONS.md for details."
)


class EmptyInput(BaseModel):
    pass


async def _myska_get(ctx: ToolContext, path: str) -> dict:
    settings = ctx.settings
    if not settings.myska_configured():
        return {"connected": False, "message": NOT_CONNECTED_MESSAGE}

    url = f"{settings.myska_api_base_url.rstrip('/')}{path}"
    headers = {"Authorization": f"Bearer {settings.myska_api_key}"}
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        return {"connected": True, "data": resp.json()}
    except httpx.HTTPError as exc:
        return {"connected": True, "error": f"MYSKA Pay request failed: {exc}"}


async def handle_myska_get_company_summary(_: EmptyInput, ctx: ToolContext) -> ToolResult:
    result = await _myska_get(ctx, "/company/summary")
    return ToolResult(success=True, data=result, message=result.get("message", "Retrieved MYSKA Pay company summary."))


async def handle_myska_get_incomplete_payrolls(_: EmptyInput, ctx: ToolContext) -> ToolResult:
    result = await _myska_get(ctx, "/payrolls/incomplete")
    return ToolResult(success=True, data=result, message=result.get("message", "Retrieved incomplete payrolls."))


async def handle_myska_get_employee_count(_: EmptyInput, ctx: ToolContext) -> ToolResult:
    result = await _myska_get(ctx, "/employees/count")
    return ToolResult(success=True, data=result, message=result.get("message", "Retrieved employee count."))


async def handle_myska_get_recent_payroll_runs(_: EmptyInput, ctx: ToolContext) -> ToolResult:
    result = await _myska_get(ctx, "/payrolls/recent")
    return ToolResult(success=True, data=result, message=result.get("message", "Retrieved recent payroll runs."))


registry.register(
    ToolDefinition(
        name="myska_get_company_summary",
        description="Get a read-only company summary from MYSKA Pay (Nova Tech's payroll platform).",
        input_model=EmptyInput,
        permission_level=PermissionLevel.GREEN,
        handler=handle_myska_get_company_summary,
    )
)
registry.register(
    ToolDefinition(
        name="myska_get_incomplete_payrolls",
        description="List incomplete payroll runs from MYSKA Pay (read-only).",
        input_model=EmptyInput,
        permission_level=PermissionLevel.GREEN,
        handler=handle_myska_get_incomplete_payrolls,
    )
)
registry.register(
    ToolDefinition(
        name="myska_get_employee_count",
        description="Get the current employee count from MYSKA Pay (read-only).",
        input_model=EmptyInput,
        permission_level=PermissionLevel.GREEN,
        handler=handle_myska_get_employee_count,
    )
)
registry.register(
    ToolDefinition(
        name="myska_get_recent_payroll_runs",
        description="List recent payroll runs from MYSKA Pay (read-only).",
        input_model=EmptyInput,
        permission_level=PermissionLevel.GREEN,
        handler=handle_myska_get_recent_payroll_runs,
    )
)
