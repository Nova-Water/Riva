import app.tools  # noqa: F401
from app.tools.registry import registry
from app.tools.schemas import PermissionLevel

GREEN_TOOLS = {
    "get_pc_status",
    "open_application",
    "open_website",
    "search_files",
    "read_text_file",
    "search_knowledgebase",
    "generate_social_post",
    "browser_read_page",
}

AMBER_TOOLS = {"create_document", "draft_email"}

RED_TOOLS: set[str] = set()  # No red-permission tools ship executable actions in this MVP.


def test_green_tools_do_not_require_confirmation():
    for name in GREEN_TOOLS:
        assert registry.get(name).permission_level == PermissionLevel.GREEN


def test_amber_tools_require_confirmation():
    for name in AMBER_TOOLS:
        assert registry.get(name).permission_level == PermissionLevel.AMBER


def test_no_tool_is_unclassified():
    for tool in registry.list_all():
        assert tool.permission_level in (PermissionLevel.GREEN, PermissionLevel.AMBER, PermissionLevel.RED)


def test_mvp_ships_no_red_tools():
    red = [t.name for t in registry.list_all() if t.permission_level == PermissionLevel.RED]
    assert red == list(RED_TOOLS)
