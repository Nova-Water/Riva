"""Structured agent output schemas. The LLM must return JSON matching one of these shapes.

We never execute freeform text as a command. Every LLM response is parsed
and validated against these Pydantic models before anything happens.
"""
from __future__ import annotations

from typing import Any, Literal, Optional, Union

from pydantic import BaseModel, Field, TypeAdapter, ValidationError


class MessageAction(BaseModel):
    type: Literal["message"]
    content: str


class ToolCallAction(BaseModel):
    type: Literal["tool_call"]
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class ConfirmationRequiredAction(BaseModel):
    type: Literal["confirmation_required"]
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    confirmation_message: str


AgentAction = Union[MessageAction, ToolCallAction, ConfirmationRequiredAction]

_adapter: TypeAdapter[AgentAction] = TypeAdapter(
    Union[MessageAction, ToolCallAction, ConfirmationRequiredAction]
)


class AgentResponseParseError(Exception):
    pass


def parse_agent_action(raw_json: str) -> AgentAction:
    """Parse and validate the LLM's raw text as one of the three agent action shapes.

    Tolerates the model wrapping JSON in a markdown code fence.
    """
    text = raw_json.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
        text = text.strip()

    import json

    try:
        payload = json.loads(text)
    except (json.JSONDecodeError, ValueError) as exc:
        raise AgentResponseParseError(f"Invalid JSON returned by the model: {exc}") from exc

    try:
        return _adapter.validate_python(payload)
    except ValidationError as exc:
        raise AgentResponseParseError(f"Response did not match an expected schema: {exc}") from exc
