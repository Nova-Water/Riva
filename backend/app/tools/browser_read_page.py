"""browser_read_page: use Playwright to read an approved page's visible text (green permission).

Read-only. Never submits forms or enters credentials in the MVP.
"""
from __future__ import annotations

import base64

from pydantic import BaseModel, Field

from app.security.url_validation import UrlSecurityError, validate_url
from app.tools.registry import ToolDefinition, registry
from app.tools.schemas import PermissionLevel, ToolContext, ToolError, ToolResult

MAX_TEXT_CHARS = 4000


class BrowserReadPageInput(BaseModel):
    url: str = Field(..., description="A full http:// or https:// URL to read.")
    take_screenshot: bool = Field(default=False, description="Whether to also capture a screenshot.")


async def handle_browser_read_page(args: BrowserReadPageInput, ctx: ToolContext) -> ToolResult:
    try:
        safe_url = validate_url(args.url)
    except UrlSecurityError as exc:
        raise ToolError(str(exc)) from exc

    try:
        from playwright.async_api import async_playwright
    except ImportError as exc:
        raise ToolError(
            "Browser automation is not installed. Run 'playwright install chromium' to enable this tool."
        ) from exc

    try:
        async with async_playwright() as pw:
            try:
                browser = await pw.chromium.launch(headless=True)
            except Exception as exc:  # noqa: BLE001
                raise ToolError(
                    "The Playwright browser is not installed. Run 'playwright install chromium'."
                ) from exc

            try:
                page = await browser.new_page()
                await page.goto(safe_url, timeout=15000, wait_until="domcontentloaded")
                title = await page.title()
                text = await page.inner_text("body")
                text = text.strip()[:MAX_TEXT_CHARS]

                screenshot_b64 = None
                if args.take_screenshot:
                    screenshot_bytes = await page.screenshot(type="png")
                    screenshot_b64 = base64.b64encode(screenshot_bytes).decode("ascii")
            finally:
                await browser.close()
    except ToolError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise ToolError(f"Could not read the page: {exc}") from exc

    return ToolResult(
        success=True,
        data={
            "url": safe_url,
            "title": title,
            "text_excerpt": text,
            "screenshot_base64": screenshot_b64,
        },
        message=f"Read page: {title or safe_url}",
    )


registry.register(
    ToolDefinition(
        name="browser_read_page",
        description=(
            "Open an approved page with a headless browser and extract its visible text, title, "
            "and optionally a screenshot. Read-only: never submits forms or enters passwords."
        ),
        input_model=BrowserReadPageInput,
        permission_level=PermissionLevel.GREEN,
        handler=handle_browser_read_page,
    )
)
