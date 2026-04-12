"""Confidence scoring algorithm for RAG responses."""

from core.logging import get_logger
from core.models.query import ConfidenceResult
from core.rag.response_parser import ExtractedClaim
from core.rag.search_models import SearchResult
from core.validation.source_tier import SourceTierClassifier

log = get_logger(__name__)


class ConfidenceScorer:
    """Score the confidence of a RAG response based on source quality and coverage.

    The score is composed of four sub-scores:
    - Source coverage (0-40): how many distinct sources are cited
    - Source quality (0-30): weighted average of source tier quality
    - Claim support (0-20): ratio of claims with supporting sources
    - Consistency (0-10): presence or absence of contradictions

    Args:
        tier_classifier: Source tier classifier for weight lookups.
    """

    def __init__(self, tier_classifier: SourceTierClassifier | None = None) -> None:
        self._tier = tier_classifier or SourceTierClassifier()

    def score_response(
        self,
        answer: str,
        search_results: list[SearchResult],
        claims: list[ExtractedClaim],
        contradictions_found: bool = False,
        minor_contradictions: bool = False,
    ) -> ConfidenceResult:
        """Calculate confidence score with explanation.

        Args:
            answer: The LLM-generated answer text.
            search_results: Retrieved chunks used as context.
            claims: Extracted claims from the answer.
            contradictions_found: Whether major contradictions were detected.
            minor_contradictions: Whether minor contradictions were detected.

        Returns:
            ConfidenceResult with score 0-100, explanation, and flagged claims.
        """
        # Sub-score A: Source coverage (0-40)
        coverage_score, source_count, doc_count = self._source_coverage(search_results)

        # Sub-score B: Source quality (0-30)
        quality_score, tier_breakdown = self._source_quality(search_results)

        # Sub-score C: Claim support (0-20)
        support_score, supported, total = self._claim_support(claims)

        # Sub-score D: Consistency (0-10)
        consistency_score = self._consistency(contradictions_found, minor_contradictions)

        total_score = min(coverage_score + quality_score + support_score + consistency_score, 100.0)

        # Build explanation
        explanation_parts = [
            f"Confidence: {total_score:.0f}/100.",
            f"Based on {source_count} source chunk(s) from {doc_count} document(s).",
        ]

        if tier_breakdown:
            tier_str = ", ".join(f"{k}: {v}" for k, v in tier_breakdown.items())
            explanation_parts.append(f"Source tiers: {tier_str}.")

        if total > 0:
            explanation_parts.append(f"{supported}/{total} claims supported by sources.")

        if contradictions_found:
            explanation_parts.append("Major contradictions detected between sources.")
        elif minor_contradictions:
            explanation_parts.append("Minor discrepancies found between sources.")

        # Flagged claims (unsupported ones)
        flagged = [c.claim_text for c in claims if not c.supporting_source]

        # Alternative interpretations (if contradictions)
        alternatives: list[str] = []
        if contradictions_found or minor_contradictions:
            alternatives.append(
                "Sources provide conflicting information — consider verifying with manufacturer documentation."
            )

        return ConfidenceResult(
            score=round(total_score, 1),
            explanation=" ".join(explanation_parts),
            flagged_claims=flagged,
            alternative_interpretations=alternatives,
        )

    def _source_coverage(self, results: list[SearchResult]) -> tuple[float, int, int]:
        """Calculate source coverage sub-score (0-40)."""
        if not results:
            return 0.0, 0, 0

        source_count = len(results)
        doc_ids = {r.metadata.get("document_id", "") for r in results}
        doc_count = len(doc_ids - {""})

        # Base: 10 per source, max 30
        base = min(source_count * 10, 30)

        # Bonus 10 for multi-document coverage
        bonus = 10 if doc_count >= 2 else 0

        return float(min(base + bonus, 40)), source_count, doc_count

    def _source_quality(self, results: list[SearchResult]) -> tuple[float, dict[str, int]]:
        """Calculate source quality sub-score (0-30)."""
        if not results:
            return 0.0, {}

        from core.models.document import SourceTier

        tier_counts: dict[str, int] = {}
        total_weight = 0.0

        for r in results:
            tier_str = r.metadata.get("source_tier", "tier_4_unverified")
            try:
                tier = SourceTier(tier_str)
            except ValueError:
                tier = SourceTier.TIER_4_UNVERIFIED

            label = self._tier.get_tier_label(tier)
            tier_counts[label] = tier_counts.get(label, 0) + 1
            total_weight += self._tier.get_tier_weight(tier)

        avg_weight = total_weight / len(results)
        score = avg_weight * 30.0

        return round(score, 1), tier_counts

    def _claim_support(self, claims: list[ExtractedClaim]) -> tuple[float, int, int]:
        """Calculate claim support sub-score (0-20)."""
        if not claims:
            return 20.0, 0, 0  # No claims = nothing to verify = full marks

        supported = sum(1 for c in claims if c.supporting_source)
        total = len(claims)
        ratio = supported / total if total > 0 else 0
        score = ratio * 20.0

        return round(score, 1), supported, total

    def _consistency(self, major: bool, minor: bool) -> float:
        """Calculate consistency sub-score (0-10)."""
        if major:
            return 0.0
        if minor:
            return 5.0
        return 10.0
