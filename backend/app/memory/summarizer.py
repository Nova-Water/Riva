"""Best-effort conversation summarization for long threads.

Failure here must never break the main conversation flow — it only
keeps future LLM calls smaller.
"""
from __future__ import annotations

from app.database import crud
from app.logging_config import get_logger
from app.providers.llm.base import LLMMessage, LLMProvider, LLMProviderError

logger = get_logger("memory.summarizer")

SUMMARY_PROMPT = (
    "Summarise the following Nova Tech / RIVA conversation in under 150 words. "
    "Preserve concrete facts, decisions, and any pending tasks. Do not invent details."
)


async def summarize_conversation(conversation_id: str, llm_provider: LLMProvider) -> None:
    if not llm_provider.is_configured():
        return

    convo = crud.get_conversation(conversation_id)
    if not convo:
        return

    older_messages = crud.get_recent_messages(conversation_id, limit=200)[:-8]
    if not older_messages:
        return

    transcript = "\n".join(f"{m.role}: {m.content}" for m in older_messages)
    messages = [
        LLMMessage(role="system", content=SUMMARY_PROMPT),
        LLMMessage(role="user", content=transcript[:8000]),
    ]

    try:
        response = await llm_provider.complete(messages, timeout_seconds=20.0)
        crud.update_conversation_summary(conversation_id, response.raw_text.strip())
    except LLMProviderError as exc:
        logger.warning("Conversation summarization skipped: %s", exc)
