"""Abstract base parser and shared parse result models."""

from abc import ABC, abstractmethod
from pathlib import Path

from pydantic import BaseModel, Field


class PageContent(BaseModel):
    """Text content extracted from a single page of a document."""

    page_number: int
    text: str
    tables: list[dict] = Field(default_factory=list)


class ExtractedImage(BaseModel):
    """An image extracted from a document, with optional OCR text."""

    image_bytes: bytes
    page_number: int | None = None
    caption: str | None = None
    ocr_text: str | None = None

    model_config = {"arbitrary_types_allowed": True}


class ParseResult(BaseModel):
    """Unified result returned by all document parsers."""

    text_content: str
    pages: list[PageContent] = Field(default_factory=list)
    images: list[ExtractedImage] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)

    model_config = {"arbitrary_types_allowed": True}


class BaseParser(ABC):
    """Abstract base class for all document parsers.

    Subclasses must implement parse() which extracts content from a file
    and returns a ParseResult. Parsers must be stateless and handle
    corrupted input gracefully — never crash, always return partial
    results or a clear error in ParseResult.warnings.
    """

    @abstractmethod
    def parse(self, filepath: Path) -> ParseResult:
        """Parse a file and extract its content.

        Args:
            filepath: Path to the file to parse.

        Returns:
            ParseResult with extracted text, pages, images, and metadata.
        """
