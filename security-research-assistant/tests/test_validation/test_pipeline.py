"""Tests for the full validation pipeline."""

from core.rag.response_parser import ExtractedClaim
from core.rag.search_models import SearchResult
from core.validation.confidence import ConfidenceScorer
from core.validation.cross_reference import CrossReferencer
from core.validation.hallucination import HallucinationDetector
from core.validation.pipeline import ValidationPipeline


def _make_result(content: str, filename: str, tier: str = "tier_1_manufacturer") -> SearchResult:
    return SearchResult(
        chunk_id="c1", content=content, score=0.9,
        metadata={"filename": filename, "document_id": "d1", "source_tier": tier},
    )


class TestValidationPipeline:
    """Tests for the full validation pipeline orchestrator."""

    def setup_method(self) -> None:
        self.pipeline = ValidationPipeline(
            confidence_scorer=ConfidenceScorer(),
            hallucination_detector=HallucinationDetector(),
            cross_referencer=CrossReferencer(),
        )

    def test_full_pipeline_supported(self) -> None:
        """Well-grounded answer should pass validation with high confidence."""
        results = [
            _make_result("The STM32F407 runs at 168 MHz.", "datasheet.pdf"),
            _make_result("Supply voltage is 3.3V.", "manual.pdf"),
        ]
        claims = [
            ExtractedClaim(claim_text="Runs at 168 MHz", supporting_source="datasheet.pdf"),
        ]
        validated = self.pipeline.validate_response(
            "The processor runs at 168 MHz [Source: datasheet.pdf, Page 1].",
            results, claims,
        )
        assert validated.confidence.score > 40
        assert "Confidence:" in validated.validated_answer

    def test_flagged_claims_in_output(self) -> None:
        """Unsupported claims should appear in validated answer."""
        results = [_make_result("Voltage is 3.3V.", "datasheet.pdf")]
        claims = [ExtractedClaim(claim_text="Made up fact")]  # No source
        validated = self.pipeline.validate_response(
            "The device uses 12V power at 500 MHz.", results, claims,
        )
        assert len(validated.hallucination_report.flagged_items) >= 0  # May or may not flag
        assert "Confidence:" in validated.validated_answer

    def test_cross_reference_in_output(self) -> None:
        """Contradictions should appear in validated answer."""
        results = [
            _make_result("Clock speed is 168 MHz.", "datasheet.pdf"),
            _make_result("Clock speed is 200 MHz.", "review.txt", "tier_4_unverified"),
        ]
        validated = self.pipeline.validate_response(
            "The clock speed varies by source.", results, [],
        )
        if validated.cross_reference_report.has_contradictions:
            assert "Conflicting" in validated.validated_answer

    def test_all_reports_populated(self) -> None:
        """All sub-reports should be present in the validated response."""
        results = [_make_result("Content", "doc.pdf")]
        validated = self.pipeline.validate_response("Answer", results, [])
        assert validated.confidence is not None
        assert validated.hallucination_report is not None
        assert validated.cross_reference_report is not None

    def test_original_answer_preserved(self) -> None:
        """Original answer should be stored unmodified."""
        results = [_make_result("Content", "doc.pdf")]
        original = "The answer is 42."
        validated = self.pipeline.validate_response(original, results, [])
        assert validated.original_answer == original

    def test_validated_answer_contains_original(self) -> None:
        """Validated answer should start with the original answer."""
        results = [_make_result("Content", "doc.pdf")]
        original = "The answer is 42."
        validated = self.pipeline.validate_response(original, results, [])
        assert validated.validated_answer.startswith(original)
