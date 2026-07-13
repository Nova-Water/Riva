"""Core assistant conversation endpoints: message, confirm, cancel."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.database import crud
from app.models.api_models import (
    AssistantCancelRequest,
    AssistantConfirmRequest,
    AssistantMessageRequest,
    AssistantMessageResponse,
    TimelineStepResponse,
    ToolActivityResponse,
)
from app.security.confirmation import confirmation_store
from app.state import AppState, get_state

router = APIRouter(prefix="/assistant", tags=["assistant"])


def _to_response(conversation_id: str, result) -> AssistantMessageResponse:
    return AssistantMessageResponse(
        conversation_id=conversation_id,
        kind=result.kind,
        content=result.content,
        tool_name=result.tool_name,
        arguments=result.arguments,
        confirmation_id=result.confirmation_id,
        confirmation_message=result.confirmation_message,
        timeline=[TimelineStepResponse(label=s.label, detail=s.detail) for s in result.timeline],
        tool_activity=[ToolActivityResponse(**a) for a in result.tool_activity],
    )


@router.post("/message", response_model=AssistantMessageResponse)
async def send_message(
    payload: AssistantMessageRequest, state: AppState = Depends(get_state)
) -> AssistantMessageResponse:
    conversation_id = payload.conversation_id
    if not conversation_id:
        convo = crud.create_conversation(title=payload.text[:60])
        conversation_id = convo.id
    elif not crud.get_conversation(conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found.")

    result = await state.agent.process_user_message(conversation_id, payload.text)
    return _to_response(conversation_id, result)


@router.post("/confirm", response_model=AssistantMessageResponse)
async def confirm_action(
    payload: AssistantConfirmRequest, state: AppState = Depends(get_state)
) -> AssistantMessageResponse:
    pending = confirmation_store.pop(payload.confirmation_id)
    if not pending or pending.conversation_id != payload.conversation_id:
        raise HTTPException(
            status_code=410, detail="This confirmation has expired or was not found. Please ask RIVA again."
        )

    if not payload.approve:
        crud.record_confirmation(payload.conversation_id, pending.tool_name, pending.arguments, "rejected")
        crud.add_message(payload.conversation_id, "system", f"Action '{pending.tool_name}' was rejected by the user.", "warning")
        return AssistantMessageResponse(
            conversation_id=payload.conversation_id,
            kind="message",
            content="Understood — I won't go ahead with that action.",
            timeline=[TimelineStepResponse(label="Cancelled by user")],
        )

    crud.record_confirmation(payload.conversation_id, pending.tool_name, pending.arguments, "approved")
    result = await state.agent.execute_confirmed_tool(payload.conversation_id, pending.tool_name, pending.arguments)
    return _to_response(payload.conversation_id, result)


@router.post("/cancel")
async def cancel_task(payload: AssistantCancelRequest) -> dict:
    crud.add_message(payload.conversation_id, "system", "The current task was cancelled by the user.", "warning")
    return {"cancelled": True}
