import pytest

from app.config import get_settings
from app.security.app_allowlist import ApplicationAllowlist
from app.tools.create_document import CreateDocumentInput, handle_create_document
from app.tools.schemas import ToolContext, ToolError


@pytest.mark.asyncio
async def test_create_document_writes_file(tmp_path):
    settings = get_settings()
    settings.data_directory = tmp_path
    output_dir = settings.documents_output_directory
    output_dir.mkdir(parents=True, exist_ok=True)
    ctx = ToolContext(settings=settings, conversation_id="c1", app_allowlist=ApplicationAllowlist([]))

    result = await handle_create_document(
        CreateDocumentInput(filename="notes.md", content="# Meeting Notes"), ctx
    )

    assert result.success is True
    assert (output_dir / "notes.md").read_text() == "# Meeting Notes"


@pytest.mark.asyncio
async def test_create_document_refuses_overwrite_without_flag(tmp_path):
    settings = get_settings()
    settings.data_directory = tmp_path
    output_dir = settings.documents_output_directory
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "existing.txt").write_text("original")
    ctx = ToolContext(settings=settings, conversation_id="c1", app_allowlist=ApplicationAllowlist([]))

    with pytest.raises(ToolError):
        await handle_create_document(
            CreateDocumentInput(filename="existing.txt", content="new content", overwrite=False), ctx
        )

    assert (output_dir / "existing.txt").read_text() == "original"


@pytest.mark.asyncio
async def test_create_document_rejects_disallowed_extension(tmp_path):
    settings = get_settings()
    settings.data_directory = tmp_path
    settings.documents_output_directory.mkdir(parents=True, exist_ok=True)
    ctx = ToolContext(settings=settings, conversation_id="c1", app_allowlist=ApplicationAllowlist([]))

    with pytest.raises(ToolError):
        await handle_create_document(CreateDocumentInput(filename="script.exe", content="x"), ctx)
