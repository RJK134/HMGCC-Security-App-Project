"""Semantic document chunker that preserves structure and metadata."""

import re
from uuid import UUID, uuid4

from core.ingest.parsers.base import ParseResult
from core.logging import get_logger
from core.models.document import Chunk

log = get_logger(__name__)


def _estimate_tokens(text: str) -> int:
    """Rough token count estimate: words * 1.3."""
    return int(len(text.split()) * 1.3)


class SemanticChunker:
    """Chunk documents by semantic boundaries, preserving structure.

    Splitting hierarchy:
    1. Section headings
    2. Paragraphs (double newline)
    3. Sentences
    4. Token-level with overlap

    Tables and code blocks are kept intact as single chunks.

    Args:
        chunk_size: Target maximum tokens per chunk.
        chunk_overlap: Overlap tokens between consecutive chunks.
    """

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50) -> None:
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    def chunk_document(self, parse_result: ParseResult, document_id: UUID) -> list[Chunk]:
        """Split a parsed document into semantically meaningful chunks.

        Args:
            parse_result: Output from a document parser.
            document_id: UUID of the parent document.

        Returns:
            Ordered list of Chunk objects with full metadata.
        """
        chunks: list[Chunk] = []

        # If we have page-level data, chunk page by page
        if parse_result.pages:
            for page in parse_result.pages:
                # Tables as standalone chunks
                for table in page.tables:
                    table_text = self._table_to_text(table)
                    if table_text.strip():
                        chunks.append(self._make_chunk(
                            content=table_text,
                            document_id=document_id,
                            chunk_index=len(chunks),
                            page_number=page.page_number,
                            section_heading="[Table]",
                        ))

                # Text content split semantically
                text_chunks = self._split_text(page.text)
                for text in text_chunks:
                    heading = self._find_nearest_heading(text, page.text)
                    chunks.append(self._make_chunk(
                        content=text,
                        document_id=document_id,
                        chunk_index=len(chunks),
                        page_number=page.page_number,
                        section_heading=heading,
                    ))
        elif parse_result.text_content.strip():
            # No page structure — chunk the full text
            text_chunks = self._split_text(parse_result.text_content)
            for text in text_chunks:
                heading = self._find_nearest_heading(text, parse_result.text_content)
                chunks.append(self._make_chunk(
                    content=text,
                    document_id=document_id,
                    chunk_index=len(chunks),
                    page_number=None,
                    section_heading=heading,
                ))

        # Also chunk OCR text from images
        for img in parse_result.images:
            if img.ocr_text and img.ocr_text.strip():
                chunks.append(self._make_chunk(
                    content=f"[Image OCR]\n{img.ocr_text}",
                    document_id=document_id,
                    chunk_index=len(chunks),
                    page_number=img.page_number,
                    section_heading="[Image OCR]",
                ))

        # Apply overlap between consecutive chunks
        chunks = self._apply_overlap(chunks)

        log.info(
            "document_chunked",
            document_id=str(document_id),
            chunk_count=len(chunks),
        )
        return chunks

    def _split_text(self, text: str) -> list[str]:
        """Split text by headings, paragraphs, then sentences."""
        if not text.strip():
            return []

        # Step 1: split by headings
        sections = re.split(r"(?=^#{1,6}\s+|\n(?=#{1,6}\s+))", text, flags=re.MULTILINE)
        sections = [s.strip() for s in sections if s.strip()]

        result: list[str] = []
        for section in sections:
            if _estimate_tokens(section) <= self._chunk_size:
                result.append(section)
                continue

            # Step 2: split by paragraphs
            paragraphs = re.split(r"\n{2,}", section)
            current_chunk: list[str] = []
            current_tokens = 0

            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue
                para_tokens = _estimate_tokens(para)

                if para_tokens > self._chunk_size:
                    # Flush current
                    if current_chunk:
                        result.append("\n\n".join(current_chunk))
                        current_chunk = []
                        current_tokens = 0
                    # Step 3: split long paragraph by sentences
                    result.extend(self._split_by_sentences(para))
                elif current_tokens + para_tokens > self._chunk_size:
                    # Flush and start new
                    result.append("\n\n".join(current_chunk))
                    current_chunk = [para]
                    current_tokens = para_tokens
                else:
                    current_chunk.append(para)
                    current_tokens += para_tokens

            if current_chunk:
                result.append("\n\n".join(current_chunk))

        return [r for r in result if r.strip()]

    def _split_by_sentences(self, text: str) -> list[str]:
        """Split text by sentences, grouping to fit chunk_size."""
        sentences = re.split(r"(?<=[.!?])\s+", text)
        result: list[str] = []
        current: list[str] = []
        current_tokens = 0

        for sent in sentences:
            sent_tokens = _estimate_tokens(sent)
            if sent_tokens > self._chunk_size:
                # Extremely long sentence — force split by tokens
                if current:
                    result.append(" ".join(current))
                    current = []
                    current_tokens = 0
                words = sent.split()
                for i in range(0, len(words), self._chunk_size):
                    result.append(" ".join(words[i:i + self._chunk_size]))
            elif current_tokens + sent_tokens > self._chunk_size:
                result.append(" ".join(current))
                current = [sent]
                current_tokens = sent_tokens
            else:
                current.append(sent)
                current_tokens += sent_tokens

        if current:
            result.append(" ".join(current))

        return result

    def _apply_overlap(self, chunks: list[Chunk]) -> list[Chunk]:
        """Prepend overlap from previous chunk to each subsequent chunk."""
        if self._chunk_overlap <= 0 or len(chunks) <= 1:
            return chunks

        for i in range(1, len(chunks)):
            prev_words = chunks[i - 1].content.split()
            overlap_words = prev_words[-self._chunk_overlap:]
            if overlap_words:
                overlap_text = " ".join(overlap_words)
                chunks[i] = chunks[i].model_copy(update={
                    "content": f"{overlap_text}\n\n{chunks[i].content}",
                    "token_count": _estimate_tokens(f"{overlap_text}\n\n{chunks[i].content}"),
                })
        return chunks

    def _table_to_text(self, table: dict) -> str:
        """Convert a table dict to searchable text."""
        headers = table.get("headers", [])
        rows = table.get("rows", [])
        if not headers and not rows:
            return ""

        lines = []
        if headers:
            lines.append(" | ".join(str(h) for h in headers))
        for row in rows:
            if headers:
                pairs = [f"{h}: {v}" for h, v in zip(headers, row) if v]
                lines.append(" | ".join(pairs))
            else:
                lines.append(" | ".join(str(c) for c in row))
        return "\n".join(lines)

    def _find_nearest_heading(self, chunk_text: str, full_text: str) -> str | None:
        """Find the nearest heading above this chunk's position in the full text."""
        # Check if the chunk itself starts with a heading
        match = re.match(r"^(#{1,6}\s+.+)", chunk_text)
        if match:
            return match.group(1).strip().lstrip("#").strip()

        # Find this chunk's position and look backwards for headings
        pos = full_text.find(chunk_text[:80])  # Use first 80 chars for search
        if pos <= 0:
            return None

        preceding = full_text[:pos]
        headings = re.findall(r"^#{1,6}\s+(.+)$", preceding, re.MULTILINE)
        return headings[-1].strip() if headings else None

    def _make_chunk(
        self,
        content: str,
        document_id: UUID,
        chunk_index: int,
        page_number: int | None,
        section_heading: str | None,
    ) -> Chunk:
        """Create a Chunk model with full metadata."""
        chunk_id = uuid4()
        return Chunk(
            id=chunk_id,
            document_id=document_id,
            content=content,
            chunk_index=chunk_index,
            page_number=page_number,
            section_heading=section_heading,
            token_count=_estimate_tokens(content),
            chroma_id=f"{document_id}_{chunk_index}",
        )
