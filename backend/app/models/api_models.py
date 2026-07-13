"""Request/response models for the FastAPI API layer."""
from __future__ import annotations

import datetime as dt
from typing import Any, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    app_name: str
    app_env: str


class ProviderStatus(BaseModel):
    configured: bool
    provider: str
    detail: str = ""


class ConfigStatusResponse(BaseModel):
    llm: ProviderStatus
    voice: ProviderStatus
    stt: ProviderStatus
    myska: ProviderStatus
    novacore: ProviderStatus
    allowed_file_roots: list[str] = Field(default_factory=list)
    allowed_applications: list[str] = Field(default_factory=list)


class SystemStatusResponse(BaseModel):
    backend_connected: bool = True
    llm_connected: bool
    voice_connected: bool
    stt_available: bool
    active_task: Optional[str] = None


class AssistantMessageRequest(BaseModel):
    conversation_id: Optional[str] = None
    text: str = Field(..., min_length=1)


class TimelineStepResponse(BaseModel):
    label: str
    detail: str = ""


class ToolActivityResponse(BaseModel):
    tool_name: str
    success: bool
    message: str


class AssistantMessageResponse(BaseModel):
    conversation_id: str
    kind: str  # message | confirmation_required | error
    content: str = ""
    tool_name: Optional[str] = None
    arguments: dict[str, Any] = Field(default_factory=dict)
    confirmation_id: Optional[str] = None
    confirmation_message: str = ""
    timeline: list[TimelineStepResponse] = Field(default_factory=list)
    tool_activity: list[ToolActivityResponse] = Field(default_factory=list)


class AssistantConfirmRequest(BaseModel):
    conversation_id: str
    confirmation_id: str
    approve: bool


class AssistantCancelRequest(BaseModel):
    conversation_id: str


class TranscribeResponse(BaseModel):
    text: str
    language: Optional[str] = None
    duration_seconds: Optional[float] = None


class SynthesizeRequest(BaseModel):
    text: str = Field(..., min_length=1)


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    message_type: str
    created_at: dt.datetime


class ConversationSummary(BaseModel):
    id: str
    title: str
    created_at: dt.datetime
    updated_at: dt.datetime


class ConversationDetail(ConversationSummary):
    summary: str = ""
    messages: list[MessageOut] = Field(default_factory=list)


class DraftOut(BaseModel):
    id: str
    recipient: str
    subject: str
    body: str
    related_to: str
    created_at: dt.datetime


class ReindexResponse(BaseModel):
    documents_indexed: int


class ToolInfo(BaseModel):
    name: str
    description: str
    permission_level: str
    input_schema: dict[str, Any]


class ErrorResponse(BaseModel):
    error: str
    detail: str = ""
