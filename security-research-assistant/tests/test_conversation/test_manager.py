"""Tests for ConversationManager."""

from uuid import uuid4

import pytest

from core.conversation.manager import ConversationManager
from core.exceptions import ConversationNotFoundError
from core.models.conversation import MessageRole


class TestConversationManager:
    """Tests for conversation lifecycle management."""

    def test_create_conversation(self, conv_manager, conv_project_id) -> None:
        """Creating a conversation should return a valid Conversation."""
        conv = conv_manager.create_conversation(conv_project_id, "Test Chat")
        assert conv.title == "Test Chat"
        assert conv.project_id == conv_project_id
        assert conv.id is not None

    def test_get_conversation(self, conv_manager, conv_project_id) -> None:
        """get_conversation should return the conversation with messages."""
        created = conv_manager.create_conversation(conv_project_id, "Get Test")
        retrieved = conv_manager.get_conversation(created.id)
        assert retrieved.id == created.id
        assert retrieved.title == "Get Test"

    def test_get_nonexistent_raises(self, conv_manager) -> None:
        """get_conversation should raise ConversationNotFoundError."""
        with pytest.raises(ConversationNotFoundError):
            conv_manager.get_conversation(uuid4())

    def test_list_conversations(self, conv_manager, conv_project_id) -> None:
        """list_conversations should return all conversations for a project."""
        conv_manager.create_conversation(conv_project_id, "Conv A")
        conv_manager.create_conversation(conv_project_id, "Conv B")
        result = conv_manager.list_conversations(conv_project_id)
        assert len(result) >= 2
        assert all("title" in c for c in result)
        assert all("message_count" in c for c in result)

    def test_add_message(self, conv_manager, conv_project_id) -> None:
        """add_message should store messages with all fields."""
        conv = conv_manager.create_conversation(conv_project_id, "Msg Test")
        msg = conv_manager.add_message(conv.id, MessageRole.USER, "What is the voltage?")
        assert msg.role == MessageRole.USER
        assert msg.content == "What is the voltage?"

    def test_add_message_with_citations(self, conv_manager, conv_project_id) -> None:
        """add_message should store citations and confidence score."""
        from core.models.conversation import Citation
        conv = conv_manager.create_conversation(conv_project_id, "Citation Test")
        citation = Citation(
            document_id=uuid4(), document_name="datasheet.pdf",
            page_number=3, chunk_id="c1", relevance_score=0.9,
            excerpt="VDD = 3.3V",
        )
        msg = conv_manager.add_message(
            conv.id, MessageRole.ASSISTANT, "The voltage is 3.3V",
            citations=[citation], confidence_score=85.0,
        )
        assert msg.confidence_score == 85.0

    def test_message_to_nonexistent_raises(self, conv_manager) -> None:
        """add_message to nonexistent conversation should raise error."""
        with pytest.raises(ConversationNotFoundError):
            conv_manager.add_message(uuid4(), MessageRole.USER, "Hello")

    def test_get_context_for_query(self, conv_manager, conv_project_id) -> None:
        """get_context_for_query should return summary, recent messages, and facts."""
        conv = conv_manager.create_conversation(conv_project_id, "Context Test")

        # Add 6 messages (3 exchanges)
        for i in range(3):
            conv_manager.add_message(conv.id, MessageRole.USER, f"Question {i}")
            conv_manager.add_message(conv.id, MessageRole.ASSISTANT, f"Answer {i}")

        ctx = conv_manager.get_context_for_query(conv.id)
        assert ctx.message_count == 6
        # Should have last 4 messages
        assert len(ctx.recent_messages) == 4
        assert ctx.recent_messages[0].content == "Question 1"

    def test_summary_triggered_at_interval(self, conv_manager, conv_project_id, mock_summariser) -> None:
        """Summary should be updated after every 10 messages."""
        conv = conv_manager.create_conversation(conv_project_id, "Summary Trigger")

        # Add 10 messages
        for i in range(10):
            role = MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT
            conv_manager.add_message(conv.id, role, f"Message {i}")

        # Summariser should have been called
        mock_summariser.summarise_conversation.assert_called()

    def test_delete_conversation(self, conv_manager, conv_project_id) -> None:
        """delete_conversation should remove the conversation."""
        conv = conv_manager.create_conversation(conv_project_id, "To Delete")
        conv_manager.delete_conversation(conv.id)
        with pytest.raises(ConversationNotFoundError):
            conv_manager.get_conversation(conv.id)

    def test_delete_nonexistent_raises(self, conv_manager) -> None:
        """delete on nonexistent conversation should raise error."""
        with pytest.raises(ConversationNotFoundError):
            conv_manager.delete_conversation(uuid4())

    def test_list_order_by_updated(self, conv_manager, conv_project_id) -> None:
        """Conversations should be ordered by updated_at descending."""
        c1 = conv_manager.create_conversation(conv_project_id, "First")
        c2 = conv_manager.create_conversation(conv_project_id, "Second")

        # Add message to c1 to make it more recently updated
        conv_manager.add_message(c1.id, MessageRole.USER, "Update this one")

        result = conv_manager.list_conversations(conv_project_id)
        # c1 should be first (most recently updated)
        assert result[0]["title"] == "First"

    def test_last_message_preview(self, conv_manager, conv_project_id) -> None:
        """list_conversations should include last message preview."""
        conv = conv_manager.create_conversation(conv_project_id, "Preview Test")
        conv_manager.add_message(conv.id, MessageRole.USER, "What are the GPIO pins?")

        result = conv_manager.list_conversations(conv_project_id)
        found = [c for c in result if c["title"] == "Preview Test"]
        assert found[0]["last_message_preview"] == "What are the GPIO pins?"
