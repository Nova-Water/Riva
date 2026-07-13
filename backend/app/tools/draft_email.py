"""draft_email: generate and save a local email draft (amber permission). Never sends email."""
from __future__ import annotations

from pydantic import BaseModel, Field

from app.database.crud import save_email_draft
from app.tools.registry import ToolDefinition, registry
from app.tools.schemas import PermissionLevel, ToolContext, ToolResult


class DraftEmailInput(BaseModel):
    recipient: str = Field(..., description="Recipient name or email address.")
    subject: str = Field(..., description="Email subject line.")
    body: str = Field(..., description="Email body content.")
    related_to: str = Field(default="", description="Related customer or project, if any.")


async def handle_draft_email(args: DraftEmailInput, ctx: ToolContext) -> ToolResult:
    draft = save_email_draft(
        recipient=args.recipient, subject=args.subject, body=args.body, related_to=args.related_to
    )
    return ToolResult(
        success=True,
        data={
            "draft_id": draft.id,
            "recipient": draft.recipient,
            "subject": draft.subject,
            "created_at": draft.created_at.isoformat(),
        },
        message=f"Saved a draft email to {draft.recipient}. It has NOT been sent.",
    )


registry.register(
    ToolDefinition(
        name="draft_email",
        description=(
            "Create and save a local email draft (recipient, subject, body, related customer/project). "
            "This never sends the email."
        ),
        input_model=DraftEmailInput,
        permission_level=PermissionLevel.AMBER,
        handler=handle_draft_email,
        confirmation_template="Save a draft email to {recipient} with subject '{subject}'? This will NOT be sent.",
    )
)
