"""Conversation summarisation and key fact extraction using local LLM."""

from core.logging import get_logger
from core.models.conversation import Message
from core.rag.llm_client import OllamaClient

log = get_logger(__name__)

_SUMMARISE_PROMPT = """Summarise the following conversation between a security researcher and their research assistant.
Focus on: key findings, questions asked, technical details discovered, and the current line of investigation.
Keep the summary under 300 words.

Conversation:
{messages}"""

_UPDATE_SUMMARY_PROMPT = """Below is a summary of an ongoing conversation, followed by new messages.
Update the summary to incorporate the new information.
Preserve all key findings and technical details from the existing summary.
Keep the updated summary under 300 words.

Existing summary:
{existing_summary}

New messages:
{new_messages}"""

_EXTRACT_FACTS_PROMPT = """From the following conversation excerpt, extract the key factual findings about the product being investigated.
List each fact on a separate line, starting with "- ".
Only include concrete technical facts, not questions or speculation.

{messages}"""


def _format_messages(messages: list[Message]) -> str:
    """Format messages into a readable transcript."""
    lines = []
    for msg in messages:
        role = "Researcher" if msg.role.value == "user" else "Assistant"
        lines.append(f"{role}: {msg.content}")
    return "\n\n".join(lines)


class ConversationSummariser:
    """Generate and update conversation summaries using the local LLM.

    Args:
        ollama_client: Ollama client for LLM calls.
    """

    def __init__(self, ollama_client: OllamaClient) -> None:
        self._llm = ollama_client

    def summarise_conversation(
        self,
        messages: list[Message],
        existing_summary: str | None = None,
    ) -> str:
        """Generate or update a conversation summary.

        If existing_summary is provided, performs incremental update
        with only the newest messages. Otherwise summarises all messages.

        Args:
            messages: All conversation messages.
            existing_summary: Previous summary to update incrementally.

        Returns:
            Summary text (max 300 words).
        """
        if not messages:
            return ""

        if existing_summary:
            # Incremental: only summarise the last few messages
            new_messages = messages[-6:]  # Last 3 exchanges
            formatted = _format_messages(new_messages)
            prompt = _UPDATE_SUMMARY_PROMPT.format(
                existing_summary=existing_summary,
                new_messages=formatted,
            )
        else:
            formatted = _format_messages(messages)
            prompt = _SUMMARISE_PROMPT.format(messages=formatted)

        try:
            response = self._llm.generate(prompt, system_prompt="")
            if not isinstance(response, str):
                response = "".join(response)

            # Enforce 300-word cap
            words = response.strip().split()
            if len(words) > 300:
                response = " ".join(words[:300]) + "..."

            log.info("conversation_summarised", words=len(response.split()))
            return response.strip()

        except Exception as e:
            log.error("summarisation_failed", error=str(e))
            return existing_summary or ""

    def extract_key_facts(self, messages: list[Message]) -> list[str]:
        """Extract key factual findings from recent messages.

        Args:
            messages: Recent conversation messages to analyse.

        Returns:
            List of factual statement strings.
        """
        if not messages:
            return []

        formatted = _format_messages(messages[-6:])  # Last 3 exchanges
        prompt = _EXTRACT_FACTS_PROMPT.format(messages=formatted)

        try:
            response = self._llm.generate(prompt, system_prompt="")
            if not isinstance(response, str):
                response = "".join(response)

            # Parse bullet-point facts
            facts = []
            for line in response.strip().split("\n"):
                line = line.strip()
                if line.startswith("- "):
                    facts.append(line[2:].strip())
                elif line.startswith("* "):
                    facts.append(line[2:].strip())
                elif line and not line.startswith("#"):
                    facts.append(line)

            return [f for f in facts if len(f) > 10]  # Filter out trivially short lines

        except Exception as e:
            log.error("fact_extraction_failed", error=str(e))
            return []
