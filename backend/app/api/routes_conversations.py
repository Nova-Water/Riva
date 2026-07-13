"""Conversation history endpoints (persistent memory)."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.database import crud
from app.models.api_models import ConversationDetail, ConversationSummary, MessageOut

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=list[ConversationSummary])
async def list_conversations() -> list[ConversationSummary]:
    convos = crud.list_conversations()
    return [
        ConversationSummary(id=c.id, title=c.title, created_at=c.created_at, updated_at=c.updated_at)
        for c in convos
    ]


@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(conversation_id: str) -> ConversationDetail:
    convo = crud.get_conversation(conversation_id)
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return ConversationDetail(
        id=convo.id,
        title=convo.title,
        summary=convo.summary,
        created_at=convo.created_at,
        updated_at=convo.updated_at,
        messages=[
            MessageOut(id=m.id, role=m.role, content=m.content, message_type=m.message_type, created_at=m.created_at)
            for m in convo.messages
        ],
    )


@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str) -> dict:
    deleted = crud.delete_conversation(conversation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return {"deleted": True}
