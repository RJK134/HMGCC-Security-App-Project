"""Context assembly for LLM prompts with token budget management."""

from core.logging import get_logger
from core.rag.search_models import SearchResult

log = get_logger(__name__)

SYSTEM_PROMPT = """You are a security research assistant helping analyse industrial control systems.
You have access to a library of technical documents about the product being investigated.

RULES:
1. ONLY answer based on the provided context. Do not use knowledge not present in the sources.
2. ALWAYS cite your sources using [Source: filename, Page X] format.
3. If the context does not contain enough information, say "Insufficient information in the current library" and suggest what additional data might help.
4. If sources contain conflicting information, present BOTH viewpoints with their respective sources.
5. When uncertain, explicitly state your confidence level (high/medium/low) and explain why.
6. For technical specifications (voltages, addresses, protocols), be EXACT — do not round or approximate.
7. If the question asks about something completely outside the provided context, say so clearly.

Present your response in a clear, structured format suitable for a security researcher."""


def _estimate_tokens(text: str) -> int:
    """Rough token count: words * 1.3."""
    return int(len(text.split()) * 1.3)


class ContextBuilder:
    """Assemble the final LLM prompt from search results and conversation context.

    Manages a token budget to ensure the assembled prompt fits within
    the local LLM's context window.

    Args:
        max_tokens: Total token budget for the assembled prompt.
    """

    def __init__(self, max_tokens: int = 4096) -> None:
        self._max_tokens = max_tokens

    def build_context(
        self,
        query: str,
        results: list[SearchResult],
        conversation_summary: str | None = None,
        pinned_facts: list[str] | None = None,
    ) -> tuple[str, str]:
        """Build the system prompt and user prompt for the LLM.

        Args:
            query: User's question.
            results: Ranked search results to use as context.
            conversation_summary: Optional summary of prior conversation.
            pinned_facts: Optional list of pinned key findings.

        Returns:
            Tuple of (system_prompt, user_prompt).
        """
        # Token budget allocation
        system_tokens = _estimate_tokens(SYSTEM_PROMPT)
        question_tokens = _estimate_tokens(query) + 30  # overhead
        summary_tokens = 0
        facts_tokens = 0

        parts: list[str] = []

        # Conversation summary
        if conversation_summary:
            summary_text = f"## Previous Conversation Context\n{conversation_summary}\n"
            summary_tokens = _estimate_tokens(summary_text)
            parts.append(summary_text)

        # Pinned facts
        if pinned_facts:
            facts_text = "## Key Established Facts\n" + "\n".join(
                f"- {fact}" for fact in pinned_facts
            ) + "\n"
            facts_tokens = _estimate_tokens(facts_text)
            parts.append(facts_text)

        # Remaining budget for context chunks
        used = system_tokens + question_tokens + summary_tokens + facts_tokens + 50
        remaining = self._max_tokens - used

        # Add context chunks in relevance order until budget exhausted
        parts.append("## Retrieved Context\n")
        chunks_added = 0

        for result in results:
            filename = result.metadata.get("filename", "unknown")
            page = result.metadata.get("page_number", "?")
            heading = result.metadata.get("section_heading", "")

            source_line = f"[Source: {filename}, Page {page}"
            if heading:
                source_line += f", Section: {heading}"
            source_line += "]"

            chunk_text = f"{source_line}\n{result.content}\n---\n"
            chunk_tokens = _estimate_tokens(chunk_text)

            if chunk_tokens > remaining:
                # Truncate to fit remaining budget
                if remaining > 50:
                    words = chunk_text.split()
                    max_words = int(remaining / 1.3)
                    truncated = " ".join(words[:max_words]) + "\n[...truncated]\n---\n"
                    parts.append(truncated)
                    chunks_added += 1
                break

            parts.append(chunk_text)
            remaining -= chunk_tokens
            chunks_added += 1

        # Build user prompt
        user_prompt = "\n".join(parts) + f"\n## Question\n{query}"

        log.info(
            "context_built",
            chunks_used=chunks_added,
            total_available=len(results),
            estimated_tokens=self._max_tokens - remaining,
        )
        return SYSTEM_PROMPT, user_prompt
