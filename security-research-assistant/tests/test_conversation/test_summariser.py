"""Tests for ConversationSummariser."""

from unittest.mock import MagicMock
from uuid import uuid4

from core.conversation.summariser import ConversationSummariser
from core.models.conversation import Message, MessageRole


def _make_messages(count: int = 4) -> list[Message]:
    """Create a list of test messages."""
    msgs = []
    conv_id = uuid4()
    for i in range(count):
        role = MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT
        content = f"Question {i}" if role == MessageRole.USER else f"The answer is related to component {i}."
        msgs.append(Message(conversation_id=conv_id, role=role, content=content))
    return msgs


class TestConversationSummariser:
    """Tests for conversation summarisation and fact extraction."""

    def test_summarise_returns_string(self) -> None:
        """summarise_conversation should return a non-empty summary."""
        mock_llm = MagicMock()
        mock_llm.generate.return_value = "The researcher investigated GPIO pin configurations."

        summariser = ConversationSummariser(mock_llm)
        result = summariser.summarise_conversation(_make_messages())

        assert len(result) > 0
        assert "GPIO" in result

    def test_incremental_summarisation(self) -> None:
        """Updating an existing summary should produce a new summary."""
        mock_llm = MagicMock()
        mock_llm.generate.return_value = "Updated summary including new SPI findings."

        summariser = ConversationSummariser(mock_llm)
        result = summariser.summarise_conversation(
            _make_messages(6),
            existing_summary="Previous summary about GPIO pins.",
        )

        assert "SPI" in result
        # Verify the prompt included the existing summary
        call_args = mock_llm.generate.call_args[0][0]
        assert "Previous summary about GPIO pins" in call_args

    def test_summary_truncated_to_300_words(self) -> None:
        """Summary exceeding 300 words should be truncated."""
        mock_llm = MagicMock()
        mock_llm.generate.return_value = " ".join(["word"] * 500)

        summariser = ConversationSummariser(mock_llm)
        result = summariser.summarise_conversation(_make_messages())

        assert len(result.split()) <= 301  # 300 + "..."

    def test_summarise_empty_messages(self) -> None:
        """Empty message list should return empty string."""
        mock_llm = MagicMock()
        summariser = ConversationSummariser(mock_llm)
        assert summariser.summarise_conversation([]) == ""

    def test_summarise_handles_llm_failure(self) -> None:
        """LLM failure should return existing summary or empty string."""
        mock_llm = MagicMock()
        mock_llm.generate.side_effect = RuntimeError("LLM down")

        summariser = ConversationSummariser(mock_llm)
        result = summariser.summarise_conversation(
            _make_messages(), existing_summary="Keep this",
        )
        assert result == "Keep this"

    def test_extract_key_facts(self) -> None:
        """extract_key_facts should return a list of factual strings."""
        mock_llm = MagicMock()
        mock_llm.generate.return_value = (
            "- Main processor is STM32F407\n"
            "- Operating voltage is 3.3V\n"
            "- SPI bus runs at 42 MHz\n"
        )

        summariser = ConversationSummariser(mock_llm)
        facts = summariser.extract_key_facts(_make_messages())

        assert len(facts) == 3
        assert "STM32F407" in facts[0]

    def test_extract_facts_empty(self) -> None:
        """extract_key_facts on empty messages should return empty list."""
        mock_llm = MagicMock()
        summariser = ConversationSummariser(mock_llm)
        assert summariser.extract_key_facts([]) == []

    def test_extract_facts_handles_failure(self) -> None:
        """LLM failure during fact extraction should return empty list."""
        mock_llm = MagicMock()
        mock_llm.generate.side_effect = RuntimeError("LLM down")

        summariser = ConversationSummariser(mock_llm)
        assert summariser.extract_key_facts(_make_messages()) == []
