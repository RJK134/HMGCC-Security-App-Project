"""Validation pipeline — every LLM response passes through before display."""

from pydantic import BaseModel, Field

from core.logging import get_logger
from core.models.query import ConfidenceResult
from core.rag.response_parser import ExtractedClaim
from core.rag.search_models import SearchResult
from core.validation.confidence import ConfidenceScorer
from core.validation.cross_reference import CrossReferenceReport, CrossReferencer
from core.validation.hallucination import HallucinationDetector, HallucinationReport

log = get_logger(__name__)


class ValidatedResponse(BaseModel):
    """Complete validated response with all analysis reports."""

    original_answer: str
    validated_answer: str
    confidence: ConfidenceResult
    hallucination_report: HallucinationReport
    cross_reference_report: CrossReferenceReport


class ValidationPipeline:
    """Orchestrate validation of every LLM response.

    Runs confidence scoring, hallucination detection, and cross-referencing,
    then constructs an enriched response with inline annotations.

    Args:
        confidence_scorer: Scores response confidence.
        hallucination_detector: Detects unsupported claims.
        cross_referencer: Compares claims across sources.
    """

    def __init__(
        self,
        confidence_scorer: ConfidenceScorer,
        hallucination_detector: HallucinationDetector,
        cross_referencer: CrossReferencer,
    ) -> None:
        self._scorer = confidence_scorer
        self._detector = hallucination_detector
        self._xref = cross_referencer

    def validate_response(
        self,
        answer: str,
        search_results: list[SearchResult],
        claims: list[ExtractedClaim],
    ) -> ValidatedResponse:
        """Run the full validation pipeline on an LLM response.

        Args:
            answer: Raw LLM-generated answer.
            search_results: Retrieved context chunks.
            claims: Extracted claims from the answer.

        Returns:
            ValidatedResponse with scores, reports, and annotated answer.
        """
        # 1. Cross-reference sources
        xref = self._xref.cross_reference(search_results)

        # 2. Hallucination detection
        hallucination = self._detector.detect_hallucinations(answer, search_results)

        # 3. Confidence scoring (incorporates contradiction info)
        confidence = self._scorer.score_response(
            answer,
            search_results,
            claims,
            contradictions_found=xref.has_contradictions,
            minor_contradictions=False,
        )

        # 4. Build validated answer with annotations
        validated = self._build_validated_answer(answer, confidence, hallucination, xref)

        log.info(
            "validation_complete",
            confidence=confidence.score,
            flagged_items=len(hallucination.flagged_items),
            contradictions=len(xref.disagreements),
        )

        return ValidatedResponse(
            original_answer=answer,
            validated_answer=validated,
            confidence=confidence,
            hallucination_report=hallucination,
            cross_reference_report=xref,
        )

    def _build_validated_answer(
        self,
        answer: str,
        confidence: ConfidenceResult,
        hallucination: HallucinationReport,
        xref: CrossReferenceReport,
    ) -> str:
        """Construct the annotated answer with validation metadata."""
        parts = [answer]

        # Confidence footer
        parts.append(f"\n\n---\nConfidence: {confidence.score:.0f}/100 — {confidence.explanation}")

        # Flagged claims
        if hallucination.flagged_items:
            flags = "\n".join(
                f"- {item.claim_text}: {item.explanation}"
                for item in hallucination.flagged_items
            )
            parts.append(f"\nFlagged claims:\n{flags}")

        # Contradictions
        if xref.disagreements:
            conflicts = "\n".join(
                f"- {d.topic}: " + ", ".join(
                    f"{src} says {val}" for src, val in d.values.items()
                )
                for d in xref.disagreements
            )
            parts.append(f"\nConflicting sources detected:\n{conflicts}")

        # Alternative interpretations
        if confidence.alternative_interpretations:
            alts = "\n".join(f"- {a}" for a in confidence.alternative_interpretations)
            parts.append(f"\nAlternative interpretations:\n{alts}")

        return "\n".join(parts)
