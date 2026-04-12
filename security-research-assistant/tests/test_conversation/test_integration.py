"""Integration test: conversation flow with RAG queries and context reconstruction."""

from pathlib import Path
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from core.conversation.manager import ConversationManager
from core.conversation.memory import MemoryManager
from core.database.connection import DatabaseManager
from core.database.repositories.project_repo import ProjectRepository
from core.models.conversation import MessageRole


class TestConversationIntegration:
    """Full conversation lifecycle integration tests with mock LLM."""

    def test_full_conversation_flow(self, conv_db, conv_project_id, conv_manager, memory_manager) -> None:
        """Create conversation, add messages, pin fact, verify context."""
        # Create conversation
        conv = conv_manager.create_conversation(conv_project_id, "ICS Analysis")

        # Add 5 exchanges
        for i in range(5):
            conv_manager.add_message(conv.id, MessageRole.USER, f"Question about component {i}")
            conv_manager.add_message(conv.id, MessageRole.ASSISTANT, f"Answer about component {i} specifications.")

        # Verify messages stored
        full = conv_manager.get_conversation(conv.id)
        assert len(full.messages) == 10

        # Pin a fact
        fact = memory_manager.pin_fact(conv.id, "Main CPU runs at 168 MHz")

        # Get context for next query
        ctx = conv_manager.get_context_for_query(conv.id)
        assert ctx.message_count == 10
        assert len(ctx.recent_messages) == 4  # Last 4 messages
        assert len(ctx.pinned_facts) == 1
        assert ctx.pinned_facts[0].content == "Main CPU runs at 168 MHz"

    def test_context_after_simulated_resume(self, conv_db, conv_project_id) -> None:
        """Simulate closing and resuming a conversation after time."""
        mock_summariser = MagicMock()
        mock_summariser.summarise_conversation.return_value = "Discussed GPIO and SPI interfaces."
        manager = ConversationManager(conv_db, mock_summariser)
        memory = MemoryManager(conv_db)

        # First session: create and interact
        conv = manager.create_conversation(conv_project_id, "Long Investigation")
        for i in range(10):
            role = MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT
            manager.add_message(conv.id, role, f"Message {i}")

        memory.pin_fact(conv.id, "Key finding: firmware is unsigned")

        # Simulate "session close" — just stop using the manager

        # "Resume" — new manager instance, same DB
        new_manager = ConversationManager(conv_db, mock_summariser)
        new_memory = MemoryManager(conv_db)

        ctx = new_manager.get_context_for_query(conv.id)

        # Summary should exist (was triggered at message 10)
        assert ctx.summary is not None
        assert len(ctx.summary) > 0

        # Recent messages should be last 4
        assert len(ctx.recent_messages) == 4

        # Pinned fact must persist
        assert len(ctx.pinned_facts) == 1
        assert "firmware is unsigned" in ctx.pinned_facts[0].content

    def test_multiple_conversations_isolated(self, conv_db, conv_project_id, conv_manager, memory_manager) -> None:
        """Messages and facts from different conversations should not mix."""
        conv_a = conv_manager.create_conversation(conv_project_id, "Thread A")
        conv_b = conv_manager.create_conversation(conv_project_id, "Thread B")

        conv_manager.add_message(conv_a.id, MessageRole.USER, "Thread A question")
        conv_manager.add_message(conv_b.id, MessageRole.USER, "Thread B question")

        memory_manager.pin_fact(conv_a.id, "Fact from A")
        memory_manager.pin_fact(conv_b.id, "Fact from B")

        ctx_a = conv_manager.get_context_for_query(conv_a.id)
        ctx_b = conv_manager.get_context_for_query(conv_b.id)

        assert ctx_a.recent_messages[0].content == "Thread A question"
        assert ctx_b.recent_messages[0].content == "Thread B question"
        assert ctx_a.pinned_facts[0].content == "Fact from A"
        assert ctx_b.pinned_facts[0].content == "Fact from B"

    def test_summary_persists_across_restart(self, conv_db, conv_project_id) -> None:
        """Summary written to DB should survive manager recreation."""
        mock_summariser = MagicMock()
        mock_summariser.summarise_conversation.return_value = "Persistent summary text."

        manager = ConversationManager(conv_db, mock_summariser)
        conv = manager.create_conversation(conv_project_id, "Persistence Test")

        # Trigger summary manually
        for i in range(10):
            role = MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT
            manager.add_message(conv.id, role, f"Msg {i}")

        # New manager reads from same DB
        new_manager = ConversationManager(conv_db, None)
        ctx = new_manager.get_context_for_query(conv.id)
        assert ctx.summary is not None
        assert "Persistent" in ctx.summary
