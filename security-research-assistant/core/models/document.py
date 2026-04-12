"""Document and chunk data models."""

from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    """Supported document file types."""

    PDF = "pdf"
    IMAGE = "image"
    CODE = "code"
    TEXT = "text"
    SPREADSHEET = "spreadsheet"
    SCHEMATIC = "schematic"


class SourceTier(str, Enum):
    """Source quality classification tiers.

    Tier 1 is highest confidence (manufacturer docs), Tier 4 is lowest.
    """

    TIER_1_MANUFACTURER = "tier_1_manufacturer"
    TIER_2_ACADEMIC = "tier_2_academic"
    TIER_3_TRUSTED_FORUM = "tier_3_trusted_forum"
    TIER_4_UNVERIFIED = "tier_4_unverified"


class DocumentStatus(str, Enum):
    """Document processing lifecycle status."""

    PENDING = "pending"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"


class DocumentMetadata(BaseModel):
    """Metadata for an ingested document."""

    id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    filename: str
    filepath: Path
    filetype: DocumentType
    size_bytes: int
    status: DocumentStatus = DocumentStatus.PENDING
    source_tier: SourceTier = SourceTier.TIER_4_UNVERIFIED
    import_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    page_count: int | None = None
    metadata: dict = Field(default_factory=dict)


class Chunk(BaseModel):
    """A text chunk extracted from a document, stored in the vector database."""

    id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    content: str
    chunk_index: int
    page_number: int | None = None
    section_heading: str | None = None
    token_count: int = 0
    chroma_id: str = ""
