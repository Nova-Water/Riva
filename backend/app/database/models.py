"""SQLAlchemy ORM models for RIVA's local memory store."""
from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> dt.datetime:
    return dt.datetime.utcnow()


class Base(DeclarativeBase):
    pass


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    title: Mapped[str] = mapped_column(String(255), default="New Conversation")
    summary: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_now, onupdate=_now)

    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at"
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"))
    role: Mapped[str] = mapped_column(String(20))  # user | assistant | system | tool
    content: Mapped[str] = mapped_column(Text, default="")
    message_type: Mapped[str] = mapped_column(String(30), default="message")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_now)

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")


class ToolCall(Base):
    __tablename__ = "tool_calls"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"))
    tool_name: Mapped[str] = mapped_column(String(100))
    arguments_json: Mapped[str] = mapped_column(Text, default="{}")
    result_json: Mapped[str] = mapped_column(Text, default="{}")
    success: Mapped[bool] = mapped_column(Boolean, default=False)
    permission_level: Mapped[str] = mapped_column(String(10), default="green")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_now)


class ConfirmationRecord(Base):
    __tablename__ = "confirmations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"))
    tool_name: Mapped[str] = mapped_column(String(100))
    arguments_json: Mapped[str] = mapped_column(Text, default="{}")
    decision: Mapped[str] = mapped_column(String(10), default="pending")  # approved | rejected | expired
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_now)
    resolved_at: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)


class EmailDraft(Base):
    __tablename__ = "email_drafts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    recipient: Mapped[str] = mapped_column(String(255))
    subject: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    related_to: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_now)


class AppSetting(Base):
    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value_json: Mapped[str] = mapped_column(Text, default="null")
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_now, onupdate=_now)


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    category: Mapped[str] = mapped_column(String(100))
    file_path: Mapped[str] = mapped_column(String(1024))
    title: Mapped[str] = mapped_column(String(255))
    indexed_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_now)
