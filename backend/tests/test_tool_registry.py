import pytest

import app.tools  # noqa: F401  registers all MVP tools
from app.tools.registry import ToolValidationError, registry


def test_known_tools_are_registered():
    names = {t.name for t in registry.list_all()}
    for expected in ["get_pc_status", "open_application", "open_website", "search_files", "create_document"]:
        assert expected in names


def test_unknown_tool_is_rejected():
    with pytest.raises(ToolValidationError):
        registry.get("delete_all_files")


def test_invalid_arguments_are_rejected():
    with pytest.raises(ToolValidationError):
        registry.validate_arguments("open_website", {"not_url": 123})


def test_valid_arguments_pass_validation():
    validated = registry.validate_arguments("open_website", {"url": "https://example.com"})
    assert validated.url == "https://example.com"
