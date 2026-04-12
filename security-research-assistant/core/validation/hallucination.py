"""Hallucination detection — verify LLM claims against retrieved source chunks."""

import re

from pydantic import BaseModel, Field

from core.logging import get_logger
from core.rag.llm_client import OllamaClient
from core.rag.search_models import SearchResult

log = get_logger(__name__)


class FlaggedItem(BaseModel):
    """A claim flagged as potentially hallucinated."""

    claim_text: str
    flag_type: str  # "unsupported" | "contradicted" | "unverifiable"
    explanation: str
    conflicting_source: str | None = None


class HallucinationReport(BaseModel):
    """Report of hallucination detection analysis."""

    total_claims: int = 0
    supported_claims: int = 0
    unsupported_claims: int = 0
    contradicted_claims: int = 0
    flagged_items: list[FlaggedItem] = Field(default_factory=list)


# Patterns indicating technical assertions
_TECH_ASSERTION_PATTERNS = [
    r"\d+\s*(?:V|mV|A|mA|MHz|GHz|kHz|Hz|KB|MB|GB|ms|us|ns|pin|pins|bit|bits|byte|bytes|ohm|W|mW)",
    r"(?:0x[0-9a-fA-F]+)",  # Hex addresses
    r"(?:SPI|I2C|UART|CAN|GPIO|RS-\d+|USB|JTAG|Ethernet)",
    r"(?:Modbus|OPC-UA|MQTT|BACnet|PROFINET|EtherNet/IP|DNP3)",
]

_LLM_VERIFY_PROMPT = """Given the following source material and an answer, identify any claims in the answer that are NOT supported by the source material.

Source material:
{sources}

Answer to verify:
{answer}

List each unsupported or contradicted claim on a separate line.
Format: UNSUPPORTED: claim text | REASON: why it's not in sources
Format: CONTRADICTED: claim text | REASON: source says otherwise
If all claims are supported, respond with: ALL_CLAIMS_SUPPORTED"""


class HallucinationDetector:
    """Detect unsupported or contradicted claims in LLM responses.

    Uses a two-pronged approach:
    1. Heuristic: substring/pattern matching of technical assertions
    2. LLM-assisted: prompt-based verification (optional, configurable)

    Args:
        ollama_client: Ollama client for LLM-assisted verification.
        use_llm_verification: Whether to run LLM-assisted checks (slower but better).
    """

    def __init__(
        self,
        ollama_client: OllamaClient | None = None,
        use_llm_verification: bool = False,
    ) -> None:
        self._llm = ollama_client
        self._use_llm = use_llm_verification and ollama_client is not None

    def detect_hallucinations(
        self, answer: str, retrieved_chunks: list[SearchResult]
    ) -> HallucinationReport:
        """Analyse an LLM answer for unsupported or contradicted claims.

        Args:
            answer: The LLM-generated answer text.
            retrieved_chunks: The source chunks provided as context.

        Returns:
            HallucinationReport with flagged items.
        """
        # Combine all source text for matching
        source_text = "\n".join(r.content for r in retrieved_chunks).lower()

        # Heuristic approach
        heuristic_flags = self._heuristic_check(answer, source_text, retrieved_chunks)

        # LLM-assisted approach (optional)
        llm_flags: list[FlaggedItem] = []
        if self._use_llm:
            llm_flags = self._llm_check(answer, retrieved_chunks)

        # Merge flags (deduplicate by claim text)
        all_flags = self._merge_flags(heuristic_flags, llm_flags)

        # Count totals
        total = len(self._extract_technical_sentences(answer))
        unsupported = sum(1 for f in all_flags if f.flag_type == "unsupported")
        contradicted = sum(1 for f in all_flags if f.flag_type == "contradicted")
        supported = max(total - unsupported - contradicted, 0)

        report = HallucinationReport(
            total_claims=total,
            supported_claims=supported,
            unsupported_claims=unsupported,
            contradicted_claims=contradicted,
            flagged_items=all_flags,
        )

        log.info(
            "hallucination_check_complete",
            total=total,
            supported=supported,
            flagged=len(all_flags),
        )
        return report

    def _heuristic_check(
        self, answer: str, source_text: str, chunks: list[SearchResult]
    ) -> list[FlaggedItem]:
        """Check technical assertions against source text using pattern matching."""
        flags: list[FlaggedItem] = []
        sentences = self._extract_technical_sentences(answer)

        for sentence in sentences:
            sentence_lower = sentence.lower().strip()
            if len(sentence_lower) < 15:
                continue

            # Check if key technical terms from the sentence appear in sources
            supported = self._check_sentence_support(sentence_lower, source_text)

            if not supported:
                flags.append(FlaggedItem(
                    claim_text=sentence.strip(),
                    flag_type="unsupported",
                    explanation="This claim contains technical assertions not found in the retrieved source material.",
                ))

        return flags

    def _check_sentence_support(self, sentence: str, source_text: str) -> bool:
        """Check if a sentence's key facts are supported by source text."""
        # Extract technical values from the sentence
        values = re.findall(
            r"(\d+(?:\.\d+)?)\s*(?:V|mV|A|mA|MHz|GHz|kHz|Hz|KB|MB|GB|ms|us|ns|pin|bit|byte|ohm|W|mW)",
            sentence,
            re.IGNORECASE,
        )
        hex_values = re.findall(r"0x[0-9a-fA-F]+", sentence)

        # If the sentence has specific technical values, check they appear in sources
        if values or hex_values:
            for val in values:
                if val in source_text:
                    return True
            for hv in hex_values:
                if hv.lower() in source_text:
                    return True
            return False

        # For non-numeric technical claims, check key phrases
        # Extract significant words (4+ chars, not common words)
        _COMMON = {"this", "that", "with", "from", "have", "been", "which", "their",
                    "also", "each", "used", "using", "based", "such", "more", "than",
                    "these", "some", "other", "into", "only", "when", "does", "will"}
        words = [w for w in sentence.split() if len(w) >= 4 and w not in _COMMON]

        if not words:
            return True  # Can't verify, don't flag

        # Check if at least 40% of significant words appear in sources
        matches = sum(1 for w in words if w in source_text)
        return matches / len(words) >= 0.4 if words else True

    def _extract_technical_sentences(self, text: str) -> list[str]:
        """Extract sentences containing technical assertions."""
        sentences = re.split(r"(?<=[.!?])\s+", text)
        technical = []
        for sent in sentences:
            if any(re.search(p, sent, re.IGNORECASE) for p in _TECH_ASSERTION_PATTERNS):
                technical.append(sent)
        return technical

    def _llm_check(self, answer: str, chunks: list[SearchResult]) -> list[FlaggedItem]:
        """Use the LLM to verify claims against source material."""
        if not self._llm:
            return []

        source_text = "\n---\n".join(r.content[:300] for r in chunks[:5])
        prompt = _LLM_VERIFY_PROMPT.format(sources=source_text, answer=answer)

        try:
            response = self._llm.generate(prompt, system_prompt="")
            if not isinstance(response, str):
                response = "".join(response)

            if "ALL_CLAIMS_SUPPORTED" in response:
                return []

            return self._parse_llm_verification(response)

        except Exception as e:
            log.warning("llm_verification_failed", error=str(e))
            return []

    def _parse_llm_verification(self, response: str) -> list[FlaggedItem]:
        """Parse the LLM verification response into flagged items."""
        flags: list[FlaggedItem] = []
        for line in response.strip().split("\n"):
            line = line.strip()
            if line.startswith("UNSUPPORTED:"):
                parts = line.split("|")
                claim = parts[0].replace("UNSUPPORTED:", "").strip()
                reason = parts[1].replace("REASON:", "").strip() if len(parts) > 1 else "Not found in sources"
                flags.append(FlaggedItem(
                    claim_text=claim, flag_type="unsupported", explanation=reason,
                ))
            elif line.startswith("CONTRADICTED:"):
                parts = line.split("|")
                claim = parts[0].replace("CONTRADICTED:", "").strip()
                reason = parts[1].replace("REASON:", "").strip() if len(parts) > 1 else "Contradicts source"
                flags.append(FlaggedItem(
                    claim_text=claim, flag_type="contradicted", explanation=reason,
                ))
        return flags

    def _merge_flags(
        self, heuristic: list[FlaggedItem], llm: list[FlaggedItem]
    ) -> list[FlaggedItem]:
        """Merge and deduplicate flags from both approaches."""
        seen_claims: set[str] = set()
        merged: list[FlaggedItem] = []

        # LLM flags take precedence (more detailed explanations)
        for flag in llm:
            key = flag.claim_text[:50].lower()
            if key not in seen_claims:
                seen_claims.add(key)
                merged.append(flag)

        for flag in heuristic:
            key = flag.claim_text[:50].lower()
            if key not in seen_claims:
                seen_claims.add(key)
                merged.append(flag)

        return merged
