"""Tests for semantic document chunker."""

from uuid import uuid4

from core.ingest.chunker import SemanticChunker
from core.ingest.parsers.base import PageContent, ParseResult


class TestSemanticChunker:
    """Tests for SemanticChunker."""

    def _make_result(self, text: str, pages: list[PageContent] | None = None) -> ParseResult:
        return ParseResult(
            text_content=text,
            pages=pages or [PageContent(page_number=1, text=text)],
        )

    def test_basic_chunking(self) -> None:
        """Chunker should produce chunks from text."""
        chunker = SemanticChunker(chunk_size=50, chunk_overlap=0)
        result = self._make_result("This is a test paragraph.\n\nAnother paragraph here.")
        chunks = chunker.chunk_document(result, uuid4())
        assert len(chunks) >= 1
        assert all(c.document_id is not None for c in chunks)

    def test_chunk_indices_sequential(self) -> None:
        """Chunk indices should be sequential starting from 0."""
        chunker = SemanticChunker(chunk_size=20, chunk_overlap=0)
        text = "\n\n".join(f"Paragraph {i} with enough words to make a chunk." for i in range(5))
        result = self._make_result(text)
        chunks = chunker.chunk_document(result, uuid4())
        indices = [c.chunk_index for c in chunks]
        assert indices == list(range(len(chunks)))

    def test_chroma_id_format(self) -> None:
        """Chroma IDs should follow {document_id}_{chunk_index} format."""
        chunker = SemanticChunker(chunk_size=50, chunk_overlap=0)
        doc_id = uuid4()
        result = self._make_result("Some content here.")
        chunks = chunker.chunk_document(result, doc_id)
        assert chunks[0].chroma_id == f"{doc_id}_0"

    def test_page_number_preserved(self) -> None:
        """Chunks should carry the page number from their source page."""
        chunker = SemanticChunker(chunk_size=500, chunk_overlap=0)
        pages = [
            PageContent(page_number=1, text="Page one content about processors."),
            PageContent(page_number=2, text="Page two content about memory."),
        ]
        result = ParseResult(
            text_content="Page one content about processors.\nPage two content about memory.",
            pages=pages,
        )
        chunks = chunker.chunk_document(result, uuid4())
        page_numbers = {c.page_number for c in chunks}
        assert 1 in page_numbers
        assert 2 in page_numbers

    def test_heading_extraction(self) -> None:
        """Chunker should extract section headings."""
        chunker = SemanticChunker(chunk_size=500, chunk_overlap=0)
        text = "## Interfaces\n\nSPI bus connects to sensor array.\n\n## Protocols\n\nModbus RTU over RS-485."
        result = self._make_result(text)
        chunks = chunker.chunk_document(result, uuid4())
        headings = [c.section_heading for c in chunks if c.section_heading]
        assert any("Interfaces" in h for h in headings) or any("Protocols" in h for h in headings)

    def test_overlap_applied(self) -> None:
        """Overlap tokens from previous chunk should appear in next chunk."""
        chunker = SemanticChunker(chunk_size=15, chunk_overlap=5)
        text = "First paragraph with several words.\n\nSecond paragraph also with words."
        result = self._make_result(text)
        chunks = chunker.chunk_document(result, uuid4())
        if len(chunks) >= 2:
            # Some words from chunk 0 should appear at start of chunk 1
            first_words = set(chunks[0].content.split()[-5:])
            second_start = set(chunks[1].content.split()[:10])
            assert first_words & second_start  # Overlap exists

    def test_token_count_populated(self) -> None:
        """Each chunk should have a non-zero token count."""
        chunker = SemanticChunker(chunk_size=500, chunk_overlap=0)
        result = self._make_result("Content with multiple words for token counting.")
        chunks = chunker.chunk_document(result, uuid4())
        assert all(c.token_count > 0 for c in chunks)

    def test_empty_text_no_chunks(self) -> None:
        """Empty text should produce no chunks."""
        chunker = SemanticChunker()
        result = self._make_result("", pages=[])
        chunks = chunker.chunk_document(result, uuid4())
        assert len(chunks) == 0

    def test_table_as_single_chunk(self) -> None:
        """Tables should be kept as individual chunks."""
        chunker = SemanticChunker(chunk_size=50, chunk_overlap=0)
        pages = [PageContent(
            page_number=1,
            text="Some text",
            tables=[{"headers": ["Col1", "Col2"], "rows": [["A", "B"], ["C", "D"]]}],
        )]
        result = ParseResult(text_content="Some text", pages=pages)
        chunks = chunker.chunk_document(result, uuid4())
        table_chunks = [c for c in chunks if "[Table]" in (c.section_heading or "")]
        assert len(table_chunks) >= 1
