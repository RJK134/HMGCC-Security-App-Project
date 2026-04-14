"""Parse LLM responses to extract citations, claims, and structured metadata."""

import re
from uuid import UUID

from pydantic import BaseModel, Field

from core.logging import get_logger
from core.models.conversation import Citation
from core.rag.search_models import SearchResult

log = get_logger(__name__)


class ExtractedClaim(BaseModel):
    """A factual claim extracted from an LLM response."""

    claim_text: str
    supporting_source: str | None = None
    claim_type: str = "factual"  # factual | interpretive | speculative


class ParsedResponse(BaseModel):
    """Structured parse of an LLM response."""

    answer_text: str
    citations: list[Citation] = Field(default_factory=list)
    claims: list[ExtractedClaim] = Field(default_factory=list)


# Regex for [Source: filename, Page N] or [Source: filename]
_CITATION_PATTERN = re.compile(
    r"\[Source:\s*([^,\]]+?)(?:,\s*Page\s*(\d+))?\s*(?:,\s*Section:\s*([^\]]*))?\]",
    re.IGNORECASE,
)


class ResponseParser:
    """Parse LLM responses to extract citations and factual claims."""

    def parse_response(
        self, llm_response: str, search_results: list[SearchResult]
    ) -> ParsedResponse:
        """Parse an LLM response, extracting citations and claims.

        Args:
            llm_response: Raw text response from the LLM.
            search_results: The search results that were provided as context.

        Returns:
            ParsedResponse with mapped citations and extracted claims.
        """
        citations = self._extract_citations(llm_response, search_results)

        # Fallback: if LLM didn't include [Source:] markers, generate citations
        # directly from search results so responses always have source attribution
        if not citations and search_results:
            citations = self._generate_fallback_citations(search_results)

        claims = self._extract_claims(llm_response)

        return ParsedResponse(
            answer_text=llm_response,
            citations=citations,
            claims=claims,
        )

    def _extract_citations(
        self, text: str, search_results: list[SearchResult]
    ) -> list[Citation]:
        """Extract [Source: ...] markers and map to actual search results."""
        citations: list[Citation] = []
        seen: set[str] = set()

        for match in _CITATION_PATTERN.finditer(text):
            filename = match.group(1).strip()
            page_str = match.group(2)
            page_num = int(page_str) if page_str else None

            # Deduplicate
            key = f"{filename}:{page_num}"
            if key in seen:
                continue
            seen.add(key)

            # Find matching search result (LLM may use PDF internal title, not filename)
            matched = self._find_matching_result(filename, page_num, search_results)

            # Override LLM's citation name with the real filename from metadata
            display_name = filename
            if matched:
                real_filename = matched.metadata.get("filename", "")
                if real_filename and real_filename != "unknown":
                    display_name = real_filename

            doc_id_str = matched.metadata.get("document_id", "") if matched else ""
            try:
                doc_id = UUID(doc_id_str) if doc_id_str else UUID(int=0)
            except ValueError:
                doc_id = UUID(int=0)

            citations.append(Citation(
                document_id=doc_id,
                document_name=display_name,
                page_number=page_num,
                chunk_id=matched.chunk_id if matched else "",
                relevance_score=matched.score if matched else 0.0,
                excerpt=matched.content[:150] if matched else "",
            ))

        return citations

    def _find_matching_result(
        self, filename: str, page_num: int | None, results: list[SearchResult]
    ) -> SearchResult | None:
        """Find the search result best matching a citation's filename and page."""
        best: SearchResult | None = None
        best_score = -1.0

        for result in results:
            result_filename = result.metadata.get("filename", "")
            result_page = result.metadata.get("page_number")

            # Check filename match (partial or exact)
            if filename.lower() in result_filename.lower() or result_filename.lower() in filename.lower():
                score = result.score
                # Bonus for page match
                if page_num is not None and result_page == page_num:
                    score += 0.5
                if score > best_score:
                    best = result
                    best_score = score

        return best

    def _generate_fallback_citations(
        self, search_results: list[SearchResult], max_citations: int = 5
    ) -> list[Citation]:
        """Generate citations directly from search results when LLM omits markers.

        This ensures responses always have source attribution even when the LLM
        doesn't follow the [Source: ...] instruction format.
        """
        citations: list[Citation] = []
        seen_docs: set[str] = set()

        for result in search_results[:max_citations]:
            doc_id_str = result.metadata.get("document_id", "")
            filename = result.metadata.get("filename", "unknown")
            page_num = result.metadata.get("page_number")

            # Deduplicate by document + page
            key = f"{doc_id_str}:{page_num}"
            if key in seen_docs:
                continue
            seen_docs.add(key)

            try:
                doc_id = UUID(doc_id_str) if doc_id_str else UUID(int=0)
            except ValueError:
                doc_id = UUID(int=0)

            citations.append(Citation(
                document_id=doc_id,
                document_name=filename,
                page_number=int(page_num) if page_num else None,
                chunk_id=result.chunk_id,
                relevance_score=result.score,
                excerpt=result.content[:150],
            ))

        log.info("fallback_citations_generated", count=len(citations))
        return citations

    def _extract_claims(self, text: str) -> list[ExtractedClaim]:
        """Extract factual claims from the response text.

        Splits by sentence and identifies those with technical assertions.
        """
        claims: list[ExtractedClaim] = []

        # Remove citation markers for cleaner claim extraction
        clean = _CITATION_PATTERN.sub("", text)

        # Split into sentences
        sentences = re.split(r"(?<=[.!?])\s+", clean)

        # Technical assertion patterns
        tech_patterns = [
            r"\d+\s*(?:V|mA|MHz|GHz|KB|MB|GB|ms|ns|pin|bit|byte)",  # measurements
            r"(?:SPI|I2C|UART|CAN|GPIO|RS-\d+|USB|JTAG)",  # interfaces
            r"(?:Modbus|OPC-UA|MQTT|BACnet|PROFINET)",  # protocols
            r"(?:STM32|ARM|Cortex|PIC|AVR|ESP)",  # processors
        ]

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:
                continue

            is_technical = any(
                re.search(pattern, sentence, re.IGNORECASE)
                for pattern in tech_patterns
            )

            if is_technical:
                # Check if it has a nearby source reference
                source = None
                source_match = _CITATION_PATTERN.search(text[max(0, text.find(sentence) - 50):text.find(sentence) + len(sentence) + 50])
                if source_match:
                    source = source_match.group(1).strip()

                claims.append(ExtractedClaim(
                    claim_text=sentence,
                    supporting_source=source,
                    claim_type="factual",
                ))

        return claims
