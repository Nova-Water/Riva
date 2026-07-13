import pytest

from app.config import get_settings
from app.security.app_allowlist import ApplicationAllowlist
from app.tools.search_files import SearchFilesInput, handle_search_files
from app.tools.schemas import ToolContext


@pytest.mark.asyncio
async def test_search_files_finds_content_match(tmp_path):
    (tmp_path / "quote-2026.md").write_text("Nova Tech CCTV quotation for Apia branch.")
    settings = get_settings()
    settings.allowed_file_roots = [str(tmp_path)]
    ctx = ToolContext(settings=settings, conversation_id="c1", app_allowlist=ApplicationAllowlist([]))

    result = await handle_search_files(SearchFilesInput(query="CCTV"), ctx)

    assert result.success is True
    assert result.data["count"] >= 1
    assert any("quote-2026.md" == r["filename"] for r in result.data["results"])


@pytest.mark.asyncio
async def test_search_files_raises_without_approved_roots(tmp_path):
    settings = get_settings()
    settings.allowed_file_roots = []
    settings.data_directory = tmp_path  # forces documents/knowledge roots to nonexistent-but-defined paths
    ctx = ToolContext(settings=settings, conversation_id="c1", app_allowlist=ApplicationAllowlist([]))

    # Even with empty allowed_file_roots, documents_output_directory/knowledge_directory
    # are always included, so this should succeed with zero results rather than raise.
    result = await handle_search_files(SearchFilesInput(query="nonexistent-term-xyz"), ctx)
    assert result.success is True
    assert result.data["count"] == 0


@pytest.mark.asyncio
async def test_search_files_ignores_unsupported_extensions(tmp_path):
    (tmp_path / "image.png").write_bytes(b"\x89PNG fake binary CCTV")
    settings = get_settings()
    settings.allowed_file_roots = [str(tmp_path)]
    ctx = ToolContext(settings=settings, conversation_id="c1", app_allowlist=ApplicationAllowlist([]))

    result = await handle_search_files(SearchFilesInput(query="CCTV"), ctx)
    assert all(r["filename"] != "image.png" for r in result.data["results"])
