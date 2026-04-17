"""Tests for response parser — citation extraction and claim extraction."""

from core.rag.response_parser import ResponseParser
from core.rag.search_models import SearchResult


def _make_result(chunk_id: str, filename: str, page: int = 1) -> SearchResult:
    return SearchResult(
        chunk_id=chunk_id, content="Some content",
        score=0.9,
        metadata={"document_id": "00000000-0000-0000-0000-000000000001",
                  "filename": filename, "page_number": page},
    )


class TestResponseParser:
    """Tests for ResponseParser."""

    def test_extract_citations(self) -> None:
        """Parser should extract [Source: filename, Page N] citations."""
        parser = ResponseParser()
        results = [_make_result("c1", "datasheet.pdf", 3)]
        response = "The voltage is 3.3V [Source: datasheet.pdf, Page 3]."
        parsed = parser.parse_response(response, results)
        assert len(parsed.citations) == 1
        assert parsed.citations[0].document_name == "datasheet.pdf"
        assert parsed.citations[0].page_number == 3
        assert parsed.citations[0].source_tier is None

    def test_citation_without_page(self) -> None:
        """Parser should handle citations without page numbers."""
        parser = ResponseParser()
        results = [_make_result("c1", "notes.txt")]
        response = "According to [Source: notes.txt], the protocol is Modbus."
        parsed = parser.parse_response(response, results)
        assert len(parsed.citations) == 1
        assert parsed.citations[0].page_number is None

    def test_multiple_citations(self) -> None:
        """Parser should extract multiple unique citations."""
        parser = ResponseParser()
        results = [
            _make_result("c1", "doc1.pdf", 1),
            _make_result("c2", "doc2.pdf", 5),
        ]
        response = (
            "Info from [Source: doc1.pdf, Page 1] and also [Source: doc2.pdf, Page 5]."
        )
        parsed = parser.parse_response(response, results)
        assert len(parsed.citations) == 2

    def test_deduplicates_citations(self) -> None:
        """Same citation appearing twice should only be counted once."""
        parser = ResponseParser()
        results = [_make_result("c1", "doc.pdf", 2)]
        response = "[Source: doc.pdf, Page 2] says X. Also [Source: doc.pdf, Page 2] confirms."
        parsed = parser.parse_response(response, results)
        assert len(parsed.citations) == 1

    def test_claim_extraction(self) -> None:
        """Parser should extract technical claims from the response."""
        parser = ResponseParser()
        response = (
            "The processor runs at 168 MHz. "
            "It uses SPI for sensor communication. "
            "The weather is nice today."
        )
        parsed = parser.parse_response(response, [])
        # Should find claims about MHz and SPI
        claim_texts = [c.claim_text for c in parsed.claims]
        assert any("168 MHz" in t for t in claim_texts) or any("SPI" in t for t in claim_texts)

    def test_no_citations_found(self) -> None:
        """Response without citation markers should return empty citations."""
        parser = ResponseParser()
        parsed = parser.parse_response("Just a plain answer.", [])
        assert parsed.citations == []

    def test_answer_text_preserved(self) -> None:
        """The full answer text should be preserved in the parsed response."""
        parser = ResponseParser()
        response = "The answer is 42."
        parsed = parser.parse_response(response, [])
        assert parsed.answer_text == response

    def test_source_tier_propagated(self) -> None:
        """Matched search-result metadata should flow into citations."""
        parser = ResponseParser()
        results = [
            SearchResult(
                chunk_id="c1",
                content="Some content",
                score=0.9,
                metadata={
                    "document_id": "00000000-0000-0000-0000-000000000001",
                    "filename": "datasheet.pdf",
                    "page_number": 3,
                    "source_tier": "tier_1_manufacturer",
                },
            )
        ]
        response = "The voltage is 3.3V [Source: datasheet.pdf, Page 3]."
        parsed = parser.parse_response(response, results)
        assert parsed.citations[0].source_tier == "tier_1_manufacturer"
