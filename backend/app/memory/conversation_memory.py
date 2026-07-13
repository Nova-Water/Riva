"""Recent-message window + persisted summary, so we never send the full
conversation history to the LLM on every turn.
"""
from __future__ import annotations

from app.database import crud
from app.database.models import Conversation, Message
from app.providers.llm.base import LLMMessage

RECENT_WINDOW_SIZE = 12
SUMMARY_TRIGGER_COUNT = 24


def build_context_messages(conversation: Conversation, recent_messages: list[Message]) -> list[LLMMessage]:
    """Combine the persisted summary (if any) with the recent message window."""
    context: list[LLMMessage] = []
    if conversation.summary:
        context.append(
            LLMMessage(
                role="system",
                content=f"Summary of earlier conversation so far:\n{conversation.summary}",
            )
        )
    for msg in recent_messages[-RECENT_WINDOW_SIZE:]:
        role = msg.role if msg.role in ("user", "assistant") else "user"
        context.append(LLMMessage(role=role, content=msg.content))
    return context


def should_summarize(conversation_id: str) -> bool:
    all_recent = crud.get_recent_messages(conversation_id, limit=SUMMARY_TRIGGER_COUNT + 1)
    return len(all_recent) > SUMMARY_TRIGGER_COUNT
