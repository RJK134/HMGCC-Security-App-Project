"""Tests for cross-reference engine."""

from core.rag.search_models import SearchResult
from core.validation.cross_reference import CrossReferencer


def _make_result(content: str, filename: str) -> SearchResult:
    return SearchResult(
        chunk_id="c1", content=content, score=0.9,
        metadata={"filename": filename, "document_id": "d1"},
    )


class TestCrossReferencer:
    """Tests for CrossReferencer."""

    def setup_method(self) -> None:
        self.xref = CrossReferencer()

    def test_agreement_detected(self) -> None:
        """Same spec from two sources should be an agreement."""
        results = [
            _make_result("Supply voltage is 3.3V.", "datasheet.pdf"),
            _make_result("The voltage supply is 3.3V.", "manual.pdf"),
        ]
        report = self.xref.cross_reference(results)
        assert len(report.agreements) >= 1
        assert any("voltage" in a.topic for a in report.agreements)

    def test_disagreement_detected(self) -> None:
        """Different values for same spec should be a disagreement."""
        results = [
            _make_result("Clock speed is 168 MHz.", "datasheet.pdf"),
            _make_result("Clock frequency is 200 MHz.", "review.txt"),
        ]
        report = self.xref.cross_reference(results)
        assert len(report.disagreements) >= 1
        assert report.has_contradictions is True

    def test_unique_claim(self) -> None:
        """Spec appearing in only one source should be unique."""
        results = [
            _make_result("Flash memory is 1 MB.", "datasheet.pdf"),
            _make_result("The device uses Modbus protocol.", "analysis.txt"),
        ]
        report = self.xref.cross_reference(results)
        # Flash memory only in datasheet → unique
        assert len(report.unique_claims) >= 1

    def test_empty_results(self) -> None:
        """Empty results should return empty report."""
        report = self.xref.cross_reference([])
        assert report.agreements == []
        assert report.disagreements == []
        assert report.has_contradictions is False

    def test_no_specs_extractable(self) -> None:
        """Text without extractable specs should produce empty report."""
        results = [
            _make_result("This is a general description.", "doc.pdf"),
            _make_result("Another general paragraph.", "doc2.pdf"),
        ]
        report = self.xref.cross_reference(results)
        assert len(report.agreements) == 0
        assert len(report.disagreements) == 0

    def test_multiple_specs_from_same_source(self) -> None:
        """Multiple specs from one source should each be unique claims."""
        results = [
            _make_result("Voltage is 3.3V. Clock speed is 168 MHz. Flash is 1 MB.", "datasheet.pdf"),
        ]
        report = self.xref.cross_reference(results)
        assert len(report.unique_claims) >= 2
