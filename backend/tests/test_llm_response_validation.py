import pytest

from app.agent.schemas import (
    AgentResponseParseError,
    ConfirmationRequiredAction,
    MessageAction,
    ToolCallAction,
    parse_agent_action,
)


def test_parses_message_action():
    action = parse_agent_action('{"type": "message", "content": "Hello!"}')
    assert isinstance(action, MessageAction)
    assert action.content == "Hello!"


def test_parses_tool_call_action():
    action = parse_agent_action('{"type": "tool_call", "tool_name": "get_pc_status", "arguments": {}}')
    assert isinstance(action, ToolCallAction)
    assert action.tool_name == "get_pc_status"


def test_parses_confirmation_required_action():
    raw = (
        '{"type": "confirmation_required", "tool_name": "create_document", '
        '"arguments": {"filename": "a.md"}, "confirmation_message": "Create a.md?"}'
    )
    action = parse_agent_action(raw)
    assert isinstance(action, ConfirmationRequiredAction)
    assert action.confirmation_message == "Create a.md?"


def test_strips_markdown_code_fence():
    raw = '```json\n{"type": "message", "content": "Hi"}\n```'
    action = parse_agent_action(raw)
    assert isinstance(action, MessageAction)


def test_rejects_invalid_json():
    with pytest.raises(AgentResponseParseError):
        parse_agent_action("not json at all")


def test_rejects_unknown_type():
    with pytest.raises(AgentResponseParseError):
        parse_agent_action('{"type": "shutdown_computer"}')


def test_rejects_missing_required_field():
    with pytest.raises(AgentResponseParseError):
        parse_agent_action('{"type": "tool_call"}')
