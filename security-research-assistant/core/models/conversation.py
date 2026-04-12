"""Conversation, message, and pinned fact data models."""

from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """Role of a message sender."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Citation(BaseModel):
    """A reference to a source document chunk used in an answer."""

    document_id: UUID
    document_name: str
    page_number: int | None = None
    chunk_id: str
    relevance_score: float
    excerpt: str


class Message(BaseModel):
    """A single message in a conversation."""

    id: UUID = Field(default_factory=uuid4)
    conversation_id: UUID
    role: MessageRole
    content: str
    citations: list[Citation] = Field(default_factory=list)
    confidence_score: float | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PinnedFact(BaseModel):
    """A key finding pinned by the user for persistent context."""

    id: UUID = Field(default_factory=uuid4)
    conversation_id: UUID
    content: str
    source_refs: list[Citation] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Conversation(BaseModel):
    """A conversation thread within a project."""

    id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    title: str
    summary: str | None = None
    messages: list[Message] = Field(default_factory=list)
    pinned_facts: list[PinnedFact] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
