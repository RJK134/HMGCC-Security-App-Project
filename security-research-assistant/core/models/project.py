"""Project data model."""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Project(BaseModel):
    """An investigation project grouping documents and conversations."""

    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    document_count: int = 0
    conversation_count: int = 0
