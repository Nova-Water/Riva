"""Read-only NovaCore integration adapter tools (placeholders until the real API is connected).

NovaCore is Nova Tech's business/sales/inventory platform. Read-only in this MVP.
"""
from __future__ import annotations

import httpx
from pydantic import BaseModel

from app.tools.registry import ToolDefinition, registry
from app.tools.schemas import PermissionLevel, ToolContext, ToolResult

NOT_CONNECTED_MESSAGE = (
    "The NovaCore integration is not yet connected. Add NOVACORE_API_BASE_URL and NOVACORE_API_KEY "
    "to your .env file to enable this feature. See docs/INTEGRATIONS.md for details."
)


class EmptyInput(BaseModel):
    pass


async def _novacore_get(ctx: ToolContext, path: str) -> dict:
    settings = ctx.settings
    if not settings.novacore_configured():
        return {"connected": False, "message": NOT_CONNECTED_MESSAGE}

    url = f"{settings.novacore_api_base_url.rstrip('/')}{path}"
    headers = {"Authorization": f"Bearer {settings.novacore_api_key}"}
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        return {"connected": True, "data": resp.json()}
    except httpx.HTTPError as exc:
        return {"connected": True, "error": f"NovaCore request failed: {exc}"}


async def handle_novacore_get_sales_summary(_: EmptyInput, ctx: ToolContext) -> ToolResult:
    result = await _novacore_get(ctx, "/sales/summary")
    return ToolResult(success=True, data=result, message=result.get("message", "Retrieved NovaCore sales summary."))


async def handle_novacore_get_open_invoices(_: EmptyInput, ctx: ToolContext) -> ToolResult:
    result = await _novacore_get(ctx, "/invoices/open")
    return ToolResult(success=True, data=result, message=result.get("message", "Retrieved open invoices."))


async def handle_novacore_get_low_stock_items(_: EmptyInput, ctx: ToolContext) -> ToolResult:
    result = await _novacore_get(ctx, "/inventory/low-stock")
    return ToolResult(success=True, data=result, message=result.get("message", "Retrieved low stock items."))


async def handle_novacore_get_recent_transactions(_: EmptyInput, ctx: ToolContext) -> ToolResult:
    result = await _novacore_get(ctx, "/transactions/recent")
    return ToolResult(success=True, data=result, message=result.get("message", "Retrieved recent transactions."))


registry.register(
    ToolDefinition(
        name="novacore_get_sales_summary",
        description="Get a read-only sales summary from NovaCore.",
        input_model=EmptyInput,
        permission_level=PermissionLevel.GREEN,
        handler=handle_novacore_get_sales_summary,
    )
)
registry.register(
    ToolDefinition(
        name="novacore_get_open_invoices",
        description="List open invoices from NovaCore (read-only).",
        input_model=EmptyInput,
        permission_level=PermissionLevel.GREEN,
        handler=handle_novacore_get_open_invoices,
    )
)
registry.register(
    ToolDefinition(
        name="novacore_get_low_stock_items",
        description="List low-stock inventory items from NovaCore (read-only).",
        input_model=EmptyInput,
        permission_level=PermissionLevel.GREEN,
        handler=handle_novacore_get_low_stock_items,
    )
)
registry.register(
    ToolDefinition(
        name="novacore_get_recent_transactions",
        description="List recent transactions from NovaCore (read-only).",
        input_model=EmptyInput,
        permission_level=PermissionLevel.GREEN,
        handler=handle_novacore_get_recent_transactions,
    )
)
