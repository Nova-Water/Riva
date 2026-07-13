"""generate_social_post: draft a Nova Tech social media post (green permission, no external effect)."""
from __future__ import annotations

from pydantic import BaseModel, Field

from app.tools.registry import ToolDefinition, registry
from app.tools.schemas import PermissionLevel, ToolContext, ToolResult


class GenerateSocialPostInput(BaseModel):
    service: str = Field(..., description="The Nova Tech service being promoted, e.g. 'CCTV installation'.")
    audience: str = Field(default="general Samoa small business audience", description="Target audience.")
    tone: str = Field(default="professional and friendly", description="Tone of voice.")
    promotion: str = Field(default="", description="Optional promotion or offer details.")
    call_to_action: str = Field(default="Contact Nova Tech Ltd today.", description="Call to action.")
    length: str = Field(default="short", description="'short', 'medium', or 'long'.")


def _length_guidance(length: str) -> str:
    return {
        "short": "2-3 sentences",
        "medium": "4-6 sentences",
        "long": "a full paragraph with multiple points",
    }.get(length.lower(), "2-3 sentences")


async def handle_generate_social_post(args: GenerateSocialPostInput, ctx: ToolContext) -> ToolResult:
    # This is a deterministic local draft generator (no external call). The agent may
    # further refine wording via the LLM before presenting it, but the tool itself is
    # offline and always produces a usable result.
    promo_line = f" {args.promotion}" if args.promotion else ""
    post = (
        f"Nova Tech Ltd is here for you! Looking for reliable {args.service}? "
        f"Our team proudly serves {args.audience} with a {args.tone} approach.{promo_line} "
        f"{args.call_to_action}"
    )
    return ToolResult(
        success=True,
        data={"post": post, "length_guidance": _length_guidance(args.length)},
        message="Generated a draft social media post.",
    )


registry.register(
    ToolDefinition(
        name="generate_social_post",
        description=(
            "Generate a Facebook/social media post draft for Nova Tech based on service, audience, "
            "tone, promotion, call to action, and length."
        ),
        input_model=GenerateSocialPostInput,
        permission_level=PermissionLevel.GREEN,
        handler=handle_generate_social_post,
    )
)
