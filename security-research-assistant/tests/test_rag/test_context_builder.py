"""Tests for context builder and token budget management."""

from core.rag.context_builder import SYSTEM_PROMPT, ContextBuilder
from core.rag.search_models import SearchResult


def _make_result(chunk_id: str, content: str, filename: str = "doc.pdf", page: int = 1) -> SearchResult:
    return SearchResult(
        chunk_id=chunk_id, content=content, score=0.9,
        metadata={"filename": filename, "page_number": page, "section_heading": "Test"},
    )


class TestContextBuilder:
    """Tests for ContextBuilder."""

    def test_system_prompt_always_included(self) -> None:
        """System prompt should always be returned."""
        builder = ContextBuilder(max_tokens=4096)
        system, user = builder.build_context("What is the voltage?", [])
        assert "security research assistant" in system.lower()

    def test_chunks_included_in_prompt(self) -> None:
        """Retrieved chunks should appear in the user prompt."""
        builder = ContextBuilder(max_tokens=4096)
        results = [_make_result("c1", "The voltage is 3.3V", "datasheet.pdf", 5)]
        _, user = builder.build_context("What is the voltage?", results)
        assert "3.3V" in user
        assert "datasheet.pdf" in user
        assert "Page 5" in user

    def test_question_in_prompt(self) -> None:
        """The user question should appear at the end of the prompt."""
        builder = ContextBuilder(max_tokens=4096)
        _, user = builder.build_context("What interfaces are available?", [])
        assert "What interfaces are available?" in user

    def test_conversation_summary_included(self) -> None:
        """Conversation summary should be included when provided."""
        builder = ContextBuilder(max_tokens=4096)
        _, user = builder.build_context(
            "Follow up question", [],
            conversation_summary="We discussed the main processor.",
        )
        assert "We discussed the main processor" in user

    def test_pinned_facts_included(self) -> None:
        """Pinned facts should appear in the prompt."""
        builder = ContextBuilder(max_tokens=4096)
        _, user = builder.build_context(
            "Question", [],
            pinned_facts=["Main CPU is STM32F407", "Operating at 3.3V"],
        )
        assert "STM32F407" in user
        assert "3.3V" in user

    def test_token_budget_respected(self) -> None:
        """Total prompt should not vastly exceed the token budget."""
        builder = ContextBuilder(max_tokens=500)
        long_content = "word " * 1000
        results = [_make_result(f"c{i}", long_content) for i in range(5)]
        system, user = builder.build_context("Question?", results)
        total_words = len(system.split()) + len(user.split())
        # With budget of 500 tokens (~385 words), should be in that ballpark
        assert total_words < 600  # Allow some overhead

    def test_chunks_ordered_by_relevance(self) -> None:
        """Chunks should appear in the context in relevance order."""
        builder = ContextBuilder(max_tokens=4096)
        results = [
            _make_result("first", "FIRST CHUNK", "a.pdf"),
            _make_result("second", "SECOND CHUNK", "b.pdf"),
        ]
        _, user = builder.build_context("Q?", results)
        assert user.index("FIRST CHUNK") < user.index("SECOND CHUNK")

    def test_custom_system_prompt_supported(self) -> None:
        """Builder should return a supplied system prompt override."""
        builder = ContextBuilder(max_tokens=4096, system_prompt="Custom prompt.")
        system, _ = builder.build_context("What is the voltage?", [])
        assert system == "Custom prompt."
