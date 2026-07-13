"""CRUD helper functions used by the API layer and agent."""
from __future__ import annotations

import json
from typing import Any, Optional

from sqlalchemy import delete, select

from app.database.db import session_scope
from app.database.models import Conversation, ConfirmationRecord, EmailDraft, Message, ToolCall


def create_conversation(title: str = "New Conversation") -> Conversation:
    with session_scope() as session:
        convo = Conversation(title=title)
        session.add(convo)
        session.flush()
        session.refresh(convo)
        session.expunge(convo)
        return convo


def get_conversation(conversation_id: str) -> Optional[Conversation]:
    with session_scope() as session:
        convo = session.get(Conversation, conversation_id)
        if convo:
            _ = [m.id for m in convo.messages]
            session.expunge_all()
        return convo


def list_conversations(limit: int = 50) -> list[Conversation]:
    with session_scope() as session:
        rows = session.execute(
            select(Conversation).order_by(Conversation.updated_at.desc()).limit(limit)
        ).scalars().all()
        session.expunge_all()
        return list(rows)


def delete_conversation(conversation_id: str) -> bool:
    with session_scope() as session:
        convo = session.get(Conversation, conversation_id)
        if not convo:
            return False
        session.delete(convo)
        return True


def clear_all_conversations() -> None:
    with session_scope() as session:
        session.execute(delete(Message))
        session.execute(delete(Conversation))
        session.execute(delete(ToolCall))
        session.execute(delete(ConfirmationRecord))


def add_message(conversation_id: str, role: str, content: str, message_type: str = "message") -> Message:
    with session_scope() as session:
        msg = Message(
            conversation_id=conversation_id, role=role, content=content, message_type=message_type
        )
        session.add(msg)
        convo = session.get(Conversation, conversation_id)
        if convo:
            convo.title = convo.title if convo.title != "New Conversation" else content[:60]
        session.flush()
        session.refresh(msg)
        session.expunge(msg)
        return msg


def get_recent_messages(conversation_id: str, limit: int = 20) -> list[Message]:
    with session_scope() as session:
        rows = session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        ).scalars().all()
        session.expunge_all()
        return list(reversed(rows))


def update_conversation_summary(conversation_id: str, summary: str) -> None:
    with session_scope() as session:
        convo = session.get(Conversation, conversation_id)
        if convo:
            convo.summary = summary


def record_tool_call(
    conversation_id: str,
    tool_name: str,
    arguments: dict[str, Any],
    result: dict[str, Any],
    success: bool,
    permission_level: str,
) -> ToolCall:
    with session_scope() as session:
        call = ToolCall(
            conversation_id=conversation_id,
            tool_name=tool_name,
            arguments_json=json.dumps(arguments),
            result_json=json.dumps(result, default=str),
            success=success,
            permission_level=permission_level,
        )
        session.add(call)
        session.flush()
        session.refresh(call)
        session.expunge(call)
        return call


def record_confirmation(
    conversation_id: str, tool_name: str, arguments: dict[str, Any], decision: str
) -> ConfirmationRecord:
    import datetime as dt

    with session_scope() as session:
        record = ConfirmationRecord(
            conversation_id=conversation_id,
            tool_name=tool_name,
            arguments_json=json.dumps(arguments),
            decision=decision,
            resolved_at=dt.datetime.utcnow(),
        )
        session.add(record)
        session.flush()
        session.refresh(record)
        session.expunge(record)
        return record


def save_email_draft(recipient: str, subject: str, body: str, related_to: str = "") -> EmailDraft:
    with session_scope() as session:
        draft = EmailDraft(recipient=recipient, subject=subject, body=body, related_to=related_to)
        session.add(draft)
        session.flush()
        session.refresh(draft)
        session.expunge(draft)
        return draft


def list_email_drafts(limit: int = 100) -> list[EmailDraft]:
    with session_scope() as session:
        rows = session.execute(
            select(EmailDraft).order_by(EmailDraft.created_at.desc()).limit(limit)
        ).scalars().all()
        session.expunge_all()
        return list(rows)
