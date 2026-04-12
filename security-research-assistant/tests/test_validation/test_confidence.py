"""Tests for confidence scoring algorithm."""

from core.rag.response_parser import ExtractedClaim
from core.rag.search_models import SearchResult
from core.validation.confidence import ConfidenceScorer


def _make_result(doc_id: str, tier: str = "tier_1_manufacturer") -> SearchResult:
    return SearchResult(
        chunk_id=f"{doc_id}_0", content="Test content",
        score=0.9, metadata={"document_id": doc_id, "source_tier": tier},
    )


def _make_claim(text: str, source: str | None = None) -> ExtractedClaim:
    return ExtractedClaim(claim_text=text, supporting_source=source, claim_type="factual")


class TestConfidenceScorer:
    """Tests for ConfidenceScorer."""

    def setup_method(self) -> None:
        self.scorer = ConfidenceScorer()

    def test_high_confidence_all_tier1(self) -> None:
        """All Tier 1 sources should produce high confidence."""
        results = [_make_result("d1"), _make_result("d2"), _make_result("d3")]
        claims = [_make_claim("Voltage is 3.3V", "datasheet.pdf")]
        score = self.scorer.score_response("Answer", results, claims)
        assert score.score >= 70

    def test_low_confidence_single_tier4(self) -> None:
        """Single Tier 4 source should produce low confidence."""
        results = [_make_result("d1", "tier_4_unverified")]
        claims = [_make_claim("Some claim")]  # No source → unsupported
        score = self.scorer.score_response("Answer", results, claims)
        assert score.score < 50

    def test_contradictions_reduce_score(self) -> None:
        """Major contradictions should reduce the consistency sub-score."""
        results = [_make_result("d1"), _make_result("d2")]
        claims = [_make_claim("Fact", "src")]
        without = self.scorer.score_response("A", results, claims, contradictions_found=False)
        with_contra = self.scorer.score_response("A", results, claims, contradictions_found=True)
        assert with_contra.score < without.score

    def test_explanation_is_readable(self) -> None:
        """Explanation should contain human-readable text."""
        results = [_make_result("d1")]
        score = self.scorer.score_response("Answer", results, [])
        assert "Confidence:" in score.explanation
        assert "source" in score.explanation.lower()

    def test_zero_sources(self) -> None:
        """No sources should produce 0 coverage score."""
        score = self.scorer.score_response("Answer", [], [])
        assert score.score <= 30  # quality and claim sub-scores still give some points

    def test_zero_claims(self) -> None:
        """No claims extracted = full claim support score (nothing to verify)."""
        results = [_make_result("d1")]
        score = self.scorer.score_response("Answer", results, [])
        assert score.score > 0

    def test_multi_document_bonus(self) -> None:
        """Multiple different documents should give a coverage bonus."""
        results_same = [_make_result("d1"), _make_result("d1")]
        results_diff = [_make_result("d1"), _make_result("d2")]
        score_same = self.scorer.score_response("A", results_same, [])
        score_diff = self.scorer.score_response("A", results_diff, [])
        assert score_diff.score >= score_same.score

    def test_flagged_claims_populated(self) -> None:
        """Unsupported claims should appear in flagged_claims."""
        claims = [
            _make_claim("Supported fact", "datasheet.pdf"),
            _make_claim("Unsupported fact"),  # No source
        ]
        score = self.scorer.score_response("A", [_make_result("d1")], claims)
        assert "Unsupported fact" in score.flagged_claims

    def test_score_within_bounds(self) -> None:
        """Score should always be 0-100."""
        for _ in range(5):
            results = [_make_result(f"d{i}") for i in range(10)]
            claims = [_make_claim(f"Claim {i}", f"src{i}") for i in range(10)]
            score = self.scorer.score_response("A", results, claims)
            assert 0 <= score.score <= 100
