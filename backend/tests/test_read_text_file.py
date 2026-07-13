import pytest

from app.config import get_settings
from app.security.app_allowlist import ApplicationAllowlist
from app.tools.read_text_file import ReadTextFileInput, handle_read_text_file
from app.tools.schemas import ToolContext, ToolError


@pytest.mark.asyncio
async def test_read_text_file_returns_content(tmp_path):
    target = tmp_path / "procedure.txt"
    target.write_text("Step 1: Confirm the customer's contact details.")
    settings = get_settings()
    settings.allowed_file_roots = [str(tmp_path)]
    ctx = ToolContext(settings=settings, conversation_id="c1", app_allowlist=ApplicationAllowlist([]))

    result = await handle_read_text_file(ReadTextFileInput(file_path=str(target)), ctx)

    assert result.success is True
    assert "Step 1" in result.data["content"]


@pytest.mark.asyncio
async def test_read_text_file_rejects_path_outside_roots(tmp_path):
    outside = tmp_path.parent / "outside.txt"
    outside.write_text("secret")
    settings = get_settings()
    settings.allowed_file_roots = [str(tmp_path)]
    ctx = ToolContext(settings=settings, conversation_id="c1", app_allowlist=ApplicationAllowlist([]))

    with pytest.raises(ToolError):
        await handle_read_text_file(ReadTextFileInput(file_path=str(outside)), ctx)


@pytest.mark.asyncio
async def test_read_text_file_rejects_missing_file(tmp_path):
    settings = get_settings()
    settings.allowed_file_roots = [str(tmp_path)]
    ctx = ToolContext(settings=settings, conversation_id="c1", app_allowlist=ApplicationAllowlist([]))

    with pytest.raises(ToolError):
        await handle_read_text_file(ReadTextFileInput(file_path=str(tmp_path / "missing.txt")), ctx)
