"""Tool registry introspection endpoint (used by the settings page)."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.models.api_models import ToolInfo
from app.state import AppState, get_state

router = APIRouter(tags=["tools"])


@router.get("/tools", response_model=list[ToolInfo])
async def list_tools(state: AppState = Depends(get_state)) -> list[ToolInfo]:
    return [
        ToolInfo(
            name=t.name,
            description=t.description,
            permission_level=t.permission_level.value,
            input_schema=t.json_schema(),
        )
        for t in state.tool_registry.list_all()
    ]
