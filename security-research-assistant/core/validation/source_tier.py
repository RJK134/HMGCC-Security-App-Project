"""Source quality tier classification based on filename patterns and metadata."""

import re

from core.logging import get_logger
from core.models.document import SourceTier

log = get_logger(__name__)

# Filename patterns for heuristic classification
_TIER_1_PATTERNS = [
    r"datasheet", r"manual", r"specification", r"spec[-_]?sheet",
    r"reference[-_]?manual", r"user[-_]?guide", r"product[-_]?brief",
    r"technical[-_]?reference", r"errata",
]
_TIER_2_PATTERNS = [
    r"ieee", r"paper", r"journal", r"proceedings", r"thesis",
    r"iec[-_]?\d+", r"iso[-_]?\d+", r"rfc[-_]?\d+", r"nist",
    r"academic", r"research",
]
_TIER_3_PATTERNS = [
    r"stackoverflow", r"stackexchange", r"electronics\.stack",
    r"hackaday", r"eevblog", r"allaboutcircuits",
    r"forum[-_]?trusted", r"expert[-_]?blog",
]

# Known manufacturer names
_KNOWN_MANUFACTURERS = {
    "stmicroelectronics", "texas instruments", "microchip", "nxp",
    "infineon", "analog devices", "maxim", "silicon labs", "espressif",
    "nordic semiconductor", "renesas", "bosch", "honeywell", "siemens",
    "schneider", "allen-bradley", "rockwell", "abb", "beckhoff",
}

_TIER_WEIGHTS: dict[SourceTier, float] = {
    SourceTier.TIER_1_MANUFACTURER: 1.0,
    SourceTier.TIER_2_ACADEMIC: 0.8,
    SourceTier.TIER_3_TRUSTED_FORUM: 0.5,
    SourceTier.TIER_4_UNVERIFIED: 0.3,
}

_TIER_LABELS: dict[SourceTier, str] = {
    SourceTier.TIER_1_MANUFACTURER: "Manufacturer / Official Documentation",
    SourceTier.TIER_2_ACADEMIC: "Academic / Industry Standard",
    SourceTier.TIER_3_TRUSTED_FORUM: "Trusted Technical Forum / Expert",
    SourceTier.TIER_4_UNVERIFIED: "Unverified / General Source",
}


class SourceTierClassifier:
    """Classify documents into quality tiers by filename and metadata heuristics."""

    def classify_from_metadata(self, filename: str, metadata: dict) -> SourceTier:
        """Auto-classify a document's source quality tier.

        Uses filename patterns, metadata fields, and known manufacturer lists.

        Args:
            filename: Original filename of the document.
            metadata: Parser-extracted metadata dict.

        Returns:
            Inferred SourceTier.
        """
        name_lower = filename.lower()
        author = str(metadata.get("author", "")).lower()
        title = str(metadata.get("title", "")).lower()
        combined = f"{name_lower} {author} {title}"

        # Check Tier 1 — manufacturer docs
        if any(re.search(p, combined) for p in _TIER_1_PATTERNS):
            return SourceTier.TIER_1_MANUFACTURER
        if any(mfr in combined for mfr in _KNOWN_MANUFACTURERS):
            return SourceTier.TIER_1_MANUFACTURER

        # Check Tier 2 — academic / standards
        if any(re.search(p, combined) for p in _TIER_2_PATTERNS):
            return SourceTier.TIER_2_ACADEMIC
        if metadata.get("doi"):
            return SourceTier.TIER_2_ACADEMIC

        # Check Tier 3 — trusted forums
        if any(re.search(p, combined) for p in _TIER_3_PATTERNS):
            return SourceTier.TIER_3_TRUSTED_FORUM

        return SourceTier.TIER_4_UNVERIFIED

    def get_tier_weight(self, tier: SourceTier) -> float:
        """Get the numeric weight for a source tier.

        Args:
            tier: Source quality tier.

        Returns:
            Weight from 0.3 (Tier 4) to 1.0 (Tier 1).
        """
        return _TIER_WEIGHTS.get(tier, 0.3)

    def get_tier_label(self, tier: SourceTier) -> str:
        """Get a human-readable label for a source tier.

        Args:
            tier: Source quality tier.

        Returns:
            Descriptive label string.
        """
        return _TIER_LABELS.get(tier, "Unknown")
