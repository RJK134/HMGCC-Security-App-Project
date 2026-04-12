"""Tests for MemoryManager (pinned facts)."""

from unittest.mock import MagicMock
from uuid import uuid4

from core.conversation.manager import ConversationManager
from core.conversation.memory import MemoryManager
from core.models.conversation import Citation, Message, MessageRole, PinnedFact


class TestMemoryManager:
    """Tests for pinned fact management."""

    def test_pin_fact(self, memory_manager, conv_manager, conv_project_id) -> None:
        """pin_fact should store and return a PinnedFact."""
        conv = conv_manager.create_conversation(conv_project_id, "Pin Test")
        fact = memory_manager.pin_fact(conv.id, "Main CPU is STM32F407")
        assert fact.content == "Main CPU is STM32F407"
        assert fact.id is not None

    def test_pin_fact_with_sources(self, memory_manager, conv_manager, conv_project_id) -> None:
        """pin_fact should store source references."""
        conv = conv_manager.create_conversation(conv_project_id, "Source Pin")
        citation = Citation(
            document_id=uuid4(), document_name="datasheet.pdf",
            page_number=1, chunk_id="c1", relevance_score=0.95,
            excerpt="ARM Cortex-M4",
        )
        fact = memory_manager.pin_fact(conv.id, "ARM Cortex-M4 core", [citation])
        assert len(fact.source_refs) == 1
        assert fact.source_refs[0].document_name == "datasheet.pdf"

    def test_get_pinned_facts(self, memory_manager, conv_manager, conv_project_id) -> None:
        """get_pinned_facts should return all pinned facts for a conversation."""
        conv = conv_manager.create_conversation(conv_project_id, "Get Pins")
        memory_manager.pin_fact(conv.id, "Fact 1")
        memory_manager.pin_fact(conv.id, "Fact 2")
        memory_manager.pin_fact(conv.id, "Fact 3")

        facts = memory_manager.get_pinned_facts(conv.id)
        assert len(facts) == 3

    def test_unpin_fact(self, memory_manager, conv_manager, conv_project_id) -> None:
        """unpin_fact should remove the fact."""
        conv = conv_manager.create_conversation(conv_project_id, "Unpin Test")
        fact = memory_manager.pin_fact(conv.id, "To be removed")
        memory_manager.unpin_fact(fact.id)

        facts = memory_manager.get_pinned_facts(conv.id)
        assert len(facts) == 0

    def test_format_facts_for_context(self, memory_manager, conv_manager, conv_project_id) -> None:
        """format_facts_for_context should produce formatted text."""
        conv = conv_manager.create_conversation(conv_project_id, "Format Test")
        memory_manager.pin_fact(conv.id, "VDD = 3.3V")
        memory_manager.pin_fact(conv.id, "Clock speed is 168 MHz")

        facts = memory_manager.get_pinned_facts(conv.id)
        formatted = MemoryManager.format_facts_for_context(facts)

        assert "KEY ESTABLISHED FACTS:" in formatted
        assert "VDD = 3.3V" in formatted
        assert "168 MHz" in formatted

    def test_format_empty_facts(self) -> None:
        """format_facts_for_context with no facts should return empty string."""
        assert MemoryManager.format_facts_for_context([]) == ""

    def test_format_facts_with_sources(self, memory_manager, conv_manager, conv_project_id) -> None:
        """Formatted facts should include source references when present."""
        conv = conv_manager.create_conversation(conv_project_id, "Source Format")
        citation = Citation(
            document_id=uuid4(), document_name="manual.pdf",
            page_number=5, chunk_id="c1", relevance_score=0.9,
            excerpt="test",
        )
        memory_manager.pin_fact(conv.id, "Power supply is 5V", [citation])

        facts = memory_manager.get_pinned_facts(conv.id)
        formatted = MemoryManager.format_facts_for_context(facts)

        assert "manual.pdf" in formatted
        assert "p.5" in formatted

    def test_suggest_facts_without_summariser(self, memory_manager, conv_manager, conv_project_id) -> None:
        """suggest_facts_to_pin without summariser should return empty list."""
        conv = conv_manager.create_conversation(conv_project_id, "No Summariser")
        suggestions = memory_manager.suggest_facts_to_pin(conv.id, [])
        assert suggestions == []

    def test_suggest_facts_with_summariser(self, memory_manager, conv_manager, conv_project_id, mock_summariser) -> None:
        """suggest_facts_to_pin with summariser should return extracted facts."""
        conv = conv_manager.create_conversation(conv_project_id, "With Summariser")
        msgs = [
            Message(conversation_id=conv.id, role=MessageRole.USER, content="What CPU?"),
            Message(conversation_id=conv.id, role=MessageRole.ASSISTANT, content="STM32F407"),
        ]
        suggestions = memory_manager.suggest_facts_to_pin(conv.id, msgs, mock_summariser)
        assert len(suggestions) == 3
        assert "STM32F407" in suggestions[0]
