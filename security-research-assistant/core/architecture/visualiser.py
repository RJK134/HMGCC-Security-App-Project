"""Export architecture data as structured JSON and generate LLM summaries."""

import json

from core.architecture.extractor import ExtractionResult
from core.architecture.mapper import ArchitectureGraph
from core.logging import get_logger
from core.rag.llm_client import OllamaClient

log = get_logger(__name__)

_SUMMARY_PROMPT = """Based on the following system architecture components, generate a clear technical
summary of the product's architecture. Include:
1. A brief overview of what the product appears to be
2. The main processing components and their roles
3. Communication interfaces and protocols used
4. Software stack
5. Areas where information is incomplete or uncertain

Components: {components}
Interfaces: {interfaces}
Protocols: {protocols}
Software: {software}

Write a concise 200-word architecture summary suitable for a security researcher."""


class ArchitectureVisualiser:
    """Generate architecture summaries and export data.

    Args:
        ollama_client: LLM for summary generation (optional).
    """

    def __init__(self, ollama_client: OllamaClient | None = None) -> None:
        self._llm = ollama_client

    def generate_summary(
        self, extraction: ExtractionResult, graph: ArchitectureGraph
    ) -> str:
        """Generate a natural-language architecture summary using the LLM.

        Args:
            extraction: Extracted components and interfaces.
            graph: Built architecture graph.

        Returns:
            Summary text describing the system architecture.
        """
        if self._llm is None:
            return self._fallback_summary(extraction, graph)

        prompt = _SUMMARY_PROMPT.format(
            components=", ".join(c.name for c in extraction.components),
            interfaces=", ".join(i.name for i in extraction.interfaces),
            protocols=", ".join(p.name for p in extraction.protocols),
            software=", ".join(s.name for s in extraction.software),
        )

        try:
            response = self._llm.generate(prompt, system_prompt="")
            if not isinstance(response, str):
                response = "".join(response)
            # Enforce 200-word limit
            words = response.strip().split()
            if len(words) > 250:
                response = " ".join(words[:250]) + "..."
            return response.strip()
        except Exception as e:
            log.warning("summary_generation_failed", error=str(e))
            return self._fallback_summary(extraction, graph)

    def _fallback_summary(self, extraction: ExtractionResult, graph: ArchitectureGraph) -> str:
        """Generate a basic summary without LLM."""
        parts = [f"System architecture with {len(extraction.components)} identified components."]

        if extraction.components:
            comp_names = ", ".join(c.name for c in extraction.components[:10])
            parts.append(f"Components: {comp_names}.")

        if extraction.interfaces:
            iface_names = ", ".join(i.name for i in extraction.interfaces[:10])
            parts.append(f"Interfaces: {iface_names}.")

        if extraction.protocols:
            proto_names = ", ".join(p.name for p in extraction.protocols[:10])
            parts.append(f"Protocols: {proto_names}.")

        if extraction.software:
            sw_names = ", ".join(s.name for s in extraction.software[:10])
            parts.append(f"Software: {sw_names}.")

        if graph.incomplete_areas:
            parts.append("Incomplete areas: " + "; ".join(graph.incomplete_areas))

        return " ".join(parts)

    def export_json(self, graph: ArchitectureGraph) -> str:
        """Export the architecture graph as a JSON string.

        Args:
            graph: Architecture graph to export.

        Returns:
            JSON string representation.
        """
        return graph.model_dump_json(indent=2)

    def export_dict(self, graph: ArchitectureGraph) -> dict:
        """Export the architecture graph as a Python dict.

        Args:
            graph: Architecture graph to export.

        Returns:
            Dictionary representation suitable for API responses.
        """
        return graph.model_dump(mode="json")
