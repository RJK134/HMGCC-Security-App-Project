"""User profile data model."""

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from core.models.document import SourceTier


class UserProfile(BaseModel):
    """Learned user preferences and behaviour patterns."""

    user_id: str = "default"
    topic_frequencies: dict[str, int] = Field(default_factory=dict)
    detail_preference: float = 0.5  # 0.0=concise, 1.0=detailed
    format_preference: str = "mixed"  # "prose" | "structured" | "mixed"
    preferred_source_tiers: list[SourceTier] = Field(default_factory=list)
    query_count: int = 0
    first_query_at: datetime | None = None
    last_query_at: datetime | None = None
    frequent_topics: list[str] = Field(default_factory=list)
    custom_preferences: dict = Field(default_factory=dict)


class ProactiveNotification(BaseModel):
    """A notification about relevant new content."""

    id: UUID = Field(default_factory=uuid4)
    message: str
    topic: str
    document_id: UUID
    document_name: str
    relevance_score: float
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    read: bool = False
