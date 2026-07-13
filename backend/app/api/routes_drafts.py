"""Email draft listing endpoint."""
from __future__ import annotations

from fastapi import APIRouter

from app.database import crud
from app.models.api_models import DraftOut

router = APIRouter(prefix="/drafts", tags=["drafts"])


@router.get("", response_model=list[DraftOut])
async def list_drafts() -> list[DraftOut]:
    drafts = crud.list_email_drafts()
    return [
        DraftOut(
            id=d.id, recipient=d.recipient, subject=d.subject, body=d.body,
            related_to=d.related_to, created_at=d.created_at,
        )
        for d in drafts
    ]
