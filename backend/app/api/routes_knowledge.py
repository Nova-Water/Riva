"""Knowledgebase reindex endpoint."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.models.api_models import ReindexResponse
from app.state import AppState, get_state
from app.tools.knowledgebase import reindex_knowledge_base

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.post("/reindex", response_model=ReindexResponse)
async def reindex(state: AppState = Depends(get_state)) -> ReindexResponse:
    count = reindex_knowledge_base(state.settings.knowledge_directory)
    return ReindexResponse(documents_indexed=count)
