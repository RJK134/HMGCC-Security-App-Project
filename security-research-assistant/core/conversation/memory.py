"""Long-term memory — pinned facts that persist across conversation sessions."""

from uuid import UUID

from core.database.connection import DatabaseManager
from core.database.repositories.conversation_repo import ConversationRepository
from core.logging import get_logger
from core.models.conversation import Citation, PinnedFact

log = get_logger(__name__)


class MemoryManager:
    """Manage pinned facts as long-term conversation memory.

    Pinned facts are always included in query context and never expire
    or get summarised away.

    Args:
        db: Database manager for SQLite operations.
    """

    def __init__(self, db: DatabaseManager) -> None:
        self._db = db
        self._repo = ConversationRepository()

    def pin_fact(
        self,
        conversation_id: UUID,
        content: str,
        source_refs: list[Citation] | None = None,
    ) -> PinnedFact:
        """Store a user-pinned fact for a conversation.

        Args:
            conversation_id: Conversation UUID.
            content: The factual finding to pin.
            source_refs: Source citations supporting this fact.

        Returns:
            The created PinnedFact.
        """
        conn = self._db.get_connection()
        fact = self._repo.add_pinned_fact(conn, conversation_id, content, source_refs)
        log.info("fact_pinned", conversation_id=str(conversation_id), content=content[:80])
        return fact

    def unpin_fact(self, fact_id: UUID) -> None:
        """Remove a pinned fact.

        Args:
            fact_id: PinnedFact UUID to remove.
        """
        conn = self._db.get_connection()
        conn.execute("DELETE FROM pinned_facts WHERE id = ?", (str(fact_id),))
        conn.commit()
        log.info("fact_unpinned", fact_id=str(fact_id))

    def get_pinned_facts(self, conversation_id: UUID) -> list[PinnedFact]:
        """Get all pinned facts for a conversation.

        Args:
            conversation_id: Conversation UUID.

        Returns:
            List of PinnedFact objects ordered by creation time.
        """
        conn = self._db.get_connection()
        return self._repo.get_pinned_facts(conn, conversation_id)

    def suggest_facts_to_pin(
        self,
        conversation_id: UUID,
        recent_messages: list,
        summariser: "ConversationSummariser | None" = None,
    ) -> list[str]:
        """Suggest facts from recent messages that could be pinned.

        Args:
            conversation_id: Conversation UUID.
            recent_messages: Recent messages to extract facts from.
            summariser: Optional summariser for LLM-based extraction.

        Returns:
            List of suggested fact strings.
        """
        if summariser is None:
            return []
        return summariser.extract_key_facts(recent_messages)

    @staticmethod
    def format_facts_for_context(facts: list[PinnedFact]) -> str:
        """Format pinned facts as a string for LLM prompt inclusion.

        Args:
            facts: List of PinnedFact objects.

        Returns:
            Formatted string block, or empty string if no facts.
        """
        if not facts:
            return ""

        lines = ["KEY ESTABLISHED FACTS:"]
        for fact in facts:
            source_info = ""
            if fact.source_refs:
                sources = ", ".join(
                    f"{ref.document_name} p.{ref.page_number}" if ref.page_number
                    else ref.document_name
                    for ref in fact.source_refs
                )
                source_info = f" [Source: {sources}]"
            lines.append(f"- {fact.content}{source_info}")

        return "\n".join(lines)


# Avoid circular import for type hint
from core.conversation.summariser import ConversationSummariser  # noqa: E402
