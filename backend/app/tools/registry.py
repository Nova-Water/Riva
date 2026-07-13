"""Central tool registry.

Every tool the agent may call is registered here with: a name, a
description shown to the LLM, a Pydantic input schema, a permission
level, and a handler function. The agent never executes a tool that
isn't in this registry, and every argument is validated against the
Pydantic schema before the handler runs.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Type

from pydantic import BaseModel

from app.tools.schemas import PermissionLevel, ToolContext, ToolResult

HandlerFn = Callable[[BaseModel, ToolContext], Awaitable[ToolResult]]


class ToolValidationError(Exception):
    pass


@dataclass
class ToolDefinition:
    name: str
    description: str
    input_model: Type[BaseModel]
    permission_level: PermissionLevel
    handler: HandlerFn
    confirmation_template: str = "RIVA is ready to run '{name}'."

    def build_confirmation_message(self, arguments: dict[str, Any]) -> str:
        try:
            return self.confirmation_template.format(name=self.name, **arguments)
        except Exception:
            return self.confirmation_template.format(name=self.name)

    def json_schema(self) -> dict[str, Any]:
        return self.input_model.model_json_schema()


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, definition: ToolDefinition) -> None:
        if definition.name in self._tools:
            raise ValueError(f"Tool '{definition.name}' is already registered.")
        self._tools[definition.name] = definition

    def get(self, name: str) -> ToolDefinition:
        tool = self._tools.get(name)
        if tool is None:
            raise ToolValidationError(f"Unknown tool: '{name}'.")
        return tool

    def has(self, name: str) -> bool:
        return name in self._tools

    def list_all(self) -> list[ToolDefinition]:
        return list(self._tools.values())

    def validate_arguments(self, name: str, raw_arguments: dict[str, Any]) -> BaseModel:
        tool = self.get(name)
        try:
            return tool.input_model.model_validate(raw_arguments or {})
        except Exception as exc:  # pydantic.ValidationError
            raise ToolValidationError(f"Invalid arguments for '{name}': {exc}") from exc


registry = ToolRegistry()
