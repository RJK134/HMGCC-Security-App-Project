"""Tests for hallucination detection."""

from core.rag.search_models import SearchResult
from core.validation.hallucination import HallucinationDetector


def _make_result(content: str, filename: str = "doc.pdf") -> SearchResult:
    return SearchResult(
        chunk_id="c1", content=content, score=0.9,
        metadata={"filename": filename, "document_id": "d1"},
    )


class TestHallucinationDetector:
    """Tests for HallucinationDetector."""

    def setup_method(self) -> None:
        self.detector = HallucinationDetector()

    def test_grounded_answer_no_flags(self) -> None:
        """Answer fully supported by sources should have no flags."""
        sources = [_make_result("The STM32F407 operates at 168 MHz with 3.3V supply voltage.")]
        answer = "The processor operates at 168 MHz. The supply voltage is 3.3V."
        report = self.detector.detect_hallucinations(answer, sources)
        assert report.unsupported_claims == 0

    def test_fabricated_spec_flagged(self) -> None:
        """A specification not in sources should be flagged."""
        sources = [_make_result("The STM32F407 operates at 168 MHz.")]
        answer = "The processor operates at 168 MHz. It also supports 500 MHz turbo mode."
        report = self.detector.detect_hallucinations(answer, sources)
        assert report.unsupported_claims > 0
        flagged_texts = [f.claim_text for f in report.flagged_items]
        assert any("500 MHz" in t for t in flagged_texts)

    def test_empty_sources_flags_all(self) -> None:
        """With no sources, all technical claims should be flagged."""
        answer = "The voltage is 3.3V and the clock speed is 168 MHz."
        report = self.detector.detect_hallucinations(answer, [])
        assert report.unsupported_claims > 0

    def test_non_technical_not_flagged(self) -> None:
        """Non-technical statements should not be extracted as claims."""
        sources = [_make_result("Some content here.")]
        answer = "The document provides helpful background information."
        report = self.detector.detect_hallucinations(answer, sources)
        # Pure non-technical sentences without numbers, protocols, or interfaces
        # should not be extracted as technical claims
        assert report.total_claims == 0

    def test_hex_address_in_sources_supported(self) -> None:
        """Hex addresses found in sources should be marked supported."""
        sources = [_make_result("The base address is 0x40020000 for GPIO port A.")]
        answer = "GPIO Port A is at address 0x40020000."
        report = self.detector.detect_hallucinations(answer, sources)
        assert report.unsupported_claims == 0

    def test_report_counts_correct(self) -> None:
        """Report counts should sum correctly."""
        sources = [_make_result("Supply voltage is 3.3V.")]
        answer = "The voltage is 3.3V. The current is 500 mA."
        report = self.detector.detect_hallucinations(answer, sources)
        assert report.total_claims == report.supported_claims + report.unsupported_claims + report.contradicted_claims

    def test_flag_type_set_correctly(self) -> None:
        """Flagged items should have correct flag_type."""
        sources = [_make_result("Clock is 168 MHz.")]
        answer = "Clock is 168 MHz. Memory is 2 GB."
        report = self.detector.detect_hallucinations(answer, sources)
        for item in report.flagged_items:
            assert item.flag_type in ("unsupported", "contradicted", "unverifiable")

    def test_explanation_present(self) -> None:
        """Flagged items should include an explanation."""
        sources = [_make_result("Voltage is 3.3V.")]
        answer = "The device uses 12V input power."
        report = self.detector.detect_hallucinations(answer, sources)
        if report.flagged_items:
            assert report.flagged_items[0].explanation
