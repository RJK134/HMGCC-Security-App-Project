"""Cross-reference engine — compare claims across multiple sources."""

import re
from collections import defaultdict

from pydantic import BaseModel, Field

from core.logging import get_logger
from core.rag.search_models import SearchResult

log = get_logger(__name__)


class Agreement(BaseModel):
    """A fact confirmed by multiple sources."""

    topic: str
    value: str
    sources: list[str]


class Disagreement(BaseModel):
    """Conflicting values for the same topic across sources."""

    topic: str
    values: dict[str, str]  # source_name → stated value
    sources_per_value: dict[str, list[str]]  # value → list of sources


class UniqueClaim(BaseModel):
    """A claim appearing in only one source."""

    claim: str
    source: str


class CrossReferenceReport(BaseModel):
    """Report from cross-referencing multiple sources."""

    agreements: list[Agreement] = Field(default_factory=list)
    disagreements: list[Disagreement] = Field(default_factory=list)
    unique_claims: list[UniqueClaim] = Field(default_factory=list)
    has_contradictions: bool = False


# Patterns for extractable technical specifications
_SPEC_PATTERNS = [
    (r"(?:voltage|vdd|vcc|supply)\s*(?:is|=|:)\s*([\d.]+\s*V)", "voltage"),
    (r"(?:clock|frequency|speed)\s*(?:is|=|:)?\s*(?:up to\s+)?([\d.]+\s*(?:MHz|GHz|kHz))", "clock_speed"),
    (r"(?:current|consumption)\s*(?:is|=|:)\s*([\d.]+\s*(?:mA|A))", "current"),
    (r"(?:flash|rom)\s*(?:memory)?\s*(?:is|=|:)?\s*([\d.]+\s*(?:KB|MB|GB))", "flash_memory"),
    (r"(?:sram|ram)\s*(?:is|=|:)?\s*([\d.]+\s*(?:KB|MB|GB))", "ram"),
    (r"(?:temperature)\s*(?:range)?\s*(?:is|=|:)?\s*(-?[\d.]+\s*C?\s*to\s*[+-]?[\d.]+\s*C?)", "temperature"),
    (r"(?:package)\s*(?:is|=|:)?\s*([A-Z]{2,}[-]?\d+)", "package"),
    (r"(?:pins?|gpio)\s*(?:count)?\s*(?:is|=|:)?\s*(\d+)", "pin_count"),
]


class CrossReferencer:
    """Compare facts across multiple source chunks to find agreements and conflicts."""

    def cross_reference(self, search_results: list[SearchResult]) -> CrossReferenceReport:
        """Analyse search results for agreements and disagreements.

        Groups chunks by source document, extracts technical specs,
        and compares values across documents.

        Args:
            search_results: Retrieved chunks from the search pipeline.

        Returns:
            CrossReferenceReport with agreements, disagreements, and unique claims.
        """
        if not search_results:
            return CrossReferenceReport()

        # Group by document
        doc_specs: dict[str, dict[str, str]] = defaultdict(dict)

        for result in search_results:
            doc_name = result.metadata.get("filename", "unknown")
            specs = self._extract_specs(result.content)
            for topic, value in specs.items():
                doc_specs[doc_name][topic] = value

        # Compare specs across documents
        all_topics: set[str] = set()
        for specs in doc_specs.values():
            all_topics.update(specs.keys())

        agreements: list[Agreement] = []
        disagreements: list[Disagreement] = []
        unique_claims: list[UniqueClaim] = []

        for topic in sorted(all_topics):
            values_by_source: dict[str, str] = {}
            for doc_name, specs in doc_specs.items():
                if topic in specs:
                    values_by_source[doc_name] = specs[topic]

            if len(values_by_source) == 1:
                # Single source — unique claim
                source, value = next(iter(values_by_source.items()))
                unique_claims.append(UniqueClaim(
                    claim=f"{topic}: {value}", source=source,
                ))
            elif len(values_by_source) >= 2:
                # Multiple sources — check agreement
                unique_values: dict[str, list[str]] = defaultdict(list)
                for source, value in values_by_source.items():
                    normalised = self._normalise_value(value)
                    unique_values[normalised].append(source)

                if len(unique_values) == 1:
                    # All agree
                    value = next(iter(unique_values.keys()))
                    sources = next(iter(unique_values.values()))
                    agreements.append(Agreement(
                        topic=topic, value=value, sources=sources,
                    ))
                else:
                    # Disagreement
                    disagreements.append(Disagreement(
                        topic=topic,
                        values=values_by_source,
                        sources_per_value=dict(unique_values),
                    ))

        report = CrossReferenceReport(
            agreements=agreements,
            disagreements=disagreements,
            unique_claims=unique_claims,
            has_contradictions=len(disagreements) > 0,
        )

        log.info(
            "cross_reference_complete",
            agreements=len(agreements),
            disagreements=len(disagreements),
            unique=len(unique_claims),
        )
        return report

    def _extract_specs(self, text: str) -> dict[str, str]:
        """Extract technical specifications from text using regex patterns."""
        specs: dict[str, str] = {}
        for pattern, topic in _SPEC_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                specs[topic] = match.group(1).strip()
        return specs

    def _normalise_value(self, value: str) -> str:
        """Normalise a value for comparison (strip whitespace, lowercase units)."""
        v = re.sub(r"\s+", " ", value.strip())
        # Normalise units to lowercase
        v = re.sub(r"(MHz|GHz|kHz|Hz|mA|mV|KB|MB|GB)", lambda m: m.group().lower(), v)
        return v
