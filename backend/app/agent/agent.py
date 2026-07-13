"""RIVA's agent orchestration loop.

Flow per user message:
  1. Persist the user message.
  2. Build a bounded context window (summary + recent messages).
  3. Ask the LLM for a structured action (message / tool_call / confirmation_required).
  4. Validate the action against the real tool registry — the LLM's own
     classification of a tool as safe is never trusted; the registry's
     permission level always wins.
  5. Green tools execute immediately and the result is fed back to the LLM
     for a final natural-language response. Amber/red tools always stop
     and return a confirmation request instead of executing.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Optional

from app.agent.schemas import (
    AgentResponseParseError,
    ConfirmationRequiredAction,
    MessageAction,
    ToolCallAction,
    parse_agent_action,
)
from app.agent.system_prompt import build_system_prompt
from app.database import crud
from app.logging_config import get_logger
from app.memory.conversation_memory import build_context_messages, should_summarize
from app.memory.summarizer import summarize_conversation
from app.providers.llm.base import LLMMessage, LLMProvider, LLMProviderError
from app.security.app_allowlist import ApplicationAllowlist
from app.tools.registry import ToolRegistry, ToolValidationError
from app.tools.schemas import PermissionLevel, ToolContext, ToolError

logger = get_logger("agent")

MAX_TOOL_ITERATIONS = 3


@dataclass
class TimelineStep:
    label: str
    detail: str = ""


@dataclass
class AgentTurnResult:
    kind: str  # "message" | "confirmation_required" | "error"
    content: str = ""
    tool_name: Optional[str] = None
    arguments: dict[str, Any] = field(default_factory=dict)
    confirmation_id: Optional[str] = None
    confirmation_message: str = ""
    timeline: list[TimelineStep] = field(default_factory=list)
    tool_activity: list[dict[str, Any]] = field(default_factory=list)


class RivaAgent:
    def __init__(self, llm_provider: LLMProvider, tool_registry: ToolRegistry, app_allowlist: ApplicationAllowlist, settings):
        self._llm = llm_provider
        self._registry = tool_registry
        self._app_allowlist = app_allowlist
        self._settings = settings

    async def process_user_message(self, conversation_id: str, user_text: str) -> AgentTurnResult:
        timeline: list[TimelineStep] = [TimelineStep("Understanding request")]
        crud.add_message(conversation_id, "user", user_text, "message")

        if not self._llm.is_configured():
            return AgentTurnResult(
                kind="message",
                content=(
                    "I'm running in a limited mode right now because no LLM provider is configured. "
                    "Add LLM_API_KEY, LLM_MODEL (and optionally LLM_BASE_URL) to your .env file to enable "
                    "full conversation."
                ),
                timeline=timeline + [TimelineStep("LLM not configured")],
            )

        tool_activity: list[dict[str, Any]] = []

        for iteration in range(MAX_TOOL_ITERATIONS):
            timeline.append(TimelineStep("Checking permissions" if iteration else "Preparing response"))
            try:
                action = await self._ask_llm(conversation_id)
            except LLMProviderError as exc:
                logger.warning("LLM error: %s", exc)
                return AgentTurnResult(
                    kind="error", content=str(exc), timeline=timeline, tool_activity=tool_activity
                )
            except AgentResponseParseError as exc:
                logger.warning("Agent parse error: %s", exc)
                return AgentTurnResult(
                    kind="error",
                    content="RIVA received an unexpected response internally and could not continue safely.",
                    timeline=timeline,
                    tool_activity=tool_activity,
                )

            if isinstance(action, MessageAction):
                crud.add_message(conversation_id, "assistant", action.content, "message")
                timeline.append(TimelineStep("Completed"))
                if should_summarize(conversation_id):
                    await summarize_conversation(conversation_id, self._llm)
                return AgentTurnResult(
                    kind="message", content=action.content, timeline=timeline, tool_activity=tool_activity
                )

            if isinstance(action, ConfirmationRequiredAction):
                return self._require_confirmation(conversation_id, action.tool_name, action.arguments, action.confirmation_message, timeline, tool_activity)

            if isinstance(action, ToolCallAction):
                try:
                    tool = self._registry.get(action.tool_name)
                except ToolValidationError as exc:
                    crud.add_message(conversation_id, "system", str(exc), "error")
                    return AgentTurnResult(kind="error", content=str(exc), timeline=timeline, tool_activity=tool_activity)

                if tool.permission_level != PermissionLevel.GREEN:
                    message = tool.build_confirmation_message(action.arguments)
                    return self._require_confirmation(
                        conversation_id, action.tool_name, action.arguments, message, timeline, tool_activity
                    )

                timeline.append(TimelineStep(f"Running tool: {tool.name}"))
                result = await self._execute_tool(conversation_id, action.tool_name, action.arguments)
                tool_activity.append(
                    {"tool_name": action.tool_name, "success": result.get("success"), "message": result.get("message")}
                )
                crud.add_message(
                    conversation_id,
                    "tool",
                    json.dumps({"tool_name": action.tool_name, "result": result}, default=str),
                    "tool_activity",
                )
                # Loop again so the LLM can turn the tool result into a natural-language answer.
                continue

        timeline.append(TimelineStep("Completed"))
        fallback = "RIVA reached the maximum number of tool steps for this request. Please rephrase or simplify your request."
        crud.add_message(conversation_id, "assistant", fallback, "message")
        return AgentTurnResult(kind="message", content=fallback, timeline=timeline, tool_activity=tool_activity)

    def _require_confirmation(
        self,
        conversation_id: str,
        tool_name: str,
        arguments: dict[str, Any],
        message: str,
        timeline: list[TimelineStep],
        tool_activity: list[dict[str, Any]],
    ) -> AgentTurnResult:
        from app.security.confirmation import confirmation_store

        if not self._registry.has(tool_name):
            error = f"Unknown tool: '{tool_name}'."
            return AgentTurnResult(kind="error", content=error, timeline=timeline, tool_activity=tool_activity)

        pending = confirmation_store.create(conversation_id, tool_name, arguments, message)
        crud.add_message(conversation_id, "assistant", message, "confirmation_request")
        timeline.append(TimelineStep("Awaiting confirmation"))
        return AgentTurnResult(
            kind="confirmation_required",
            tool_name=tool_name,
            arguments=arguments,
            confirmation_id=pending.confirmation_id,
            confirmation_message=message,
            timeline=timeline,
            tool_activity=tool_activity,
        )

    async def _ask_llm(self, conversation_id: str):
        convo = crud.get_conversation(conversation_id)
        recent = crud.get_recent_messages(conversation_id)
        system_prompt = build_system_prompt(self._registry)
        messages = [LLMMessage(role="system", content=system_prompt)]
        messages.extend(build_context_messages(convo, recent))

        response = await self._llm.complete(messages)
        return parse_agent_action(response.raw_text)

    async def _execute_tool(self, conversation_id: str, tool_name: str, raw_arguments: dict[str, Any]) -> dict[str, Any]:
        tool = self._registry.get(tool_name)
        try:
            validated_args = self._registry.validate_arguments(tool_name, raw_arguments)
        except ToolValidationError as exc:
            result = {"success": False, "error": str(exc), "message": str(exc)}
            crud.record_tool_call(conversation_id, tool_name, raw_arguments, result, False, tool.permission_level.value)
            return result

        ctx = ToolContext(settings=self._settings, conversation_id=conversation_id, app_allowlist=self._app_allowlist)
        try:
            result = await tool.handler(validated_args, ctx)
            result_dict = result.to_dict()
        except ToolError as exc:
            result_dict = {"success": False, "data": None, "message": str(exc), "error": str(exc)}
        except Exception as exc:  # noqa: BLE001 - tool failures must never crash the agent
            logger.exception("Tool '%s' raised an unexpected error", tool_name)
            result_dict = {
                "success": False,
                "data": None,
                "message": "The tool failed unexpectedly.",
                "error": str(exc),
            }

        crud.record_tool_call(
            conversation_id, tool_name, raw_arguments, result_dict, result_dict.get("success", False), tool.permission_level.value
        )
        return result_dict

    async def execute_confirmed_tool(self, conversation_id: str, tool_name: str, arguments: dict[str, Any]) -> AgentTurnResult:
        """Run a tool the user has explicitly approved, then let the LLM phrase the final reply."""
        timeline = [TimelineStep("Checking permissions"), TimelineStep(f"Running tool: {tool_name}")]
        result = await self._execute_tool(conversation_id, tool_name, arguments)
        tool_activity = [{"tool_name": tool_name, "success": result.get("success"), "message": result.get("message")}]
        crud.add_message(
            conversation_id, "tool", json.dumps({"tool_name": tool_name, "result": result}, default=str), "tool_activity"
        )

        if not self._llm.is_configured():
            content = result.get("message", "Done.")
            crud.add_message(conversation_id, "assistant", content, "message")
            timeline.append(TimelineStep("Completed"))
            return AgentTurnResult(kind="message", content=content, timeline=timeline, tool_activity=tool_activity)

        try:
            action = await self._ask_llm(conversation_id)
        except (LLMProviderError, AgentResponseParseError):
            content = result.get("message", "Done.")
            crud.add_message(conversation_id, "assistant", content, "message")
            timeline.append(TimelineStep("Completed"))
            return AgentTurnResult(kind="message", content=content, timeline=timeline, tool_activity=tool_activity)

        content = action.content if isinstance(action, MessageAction) else result.get("message", "Done.")
        crud.add_message(conversation_id, "assistant", content, "message")
        timeline.append(TimelineStep("Completed"))
        return AgentTurnResult(kind="message", content=content, timeline=timeline, tool_activity=tool_activity)
