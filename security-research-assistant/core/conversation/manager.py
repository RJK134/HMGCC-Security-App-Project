"""Conversation lifecycle management — create, retrieve, message, and context."""

from uuid import UUID

from pydantic import BaseModel, Field

from core.database.connection import DatabaseManager
from core.database.repositories.conversation_repo import ConversationRepository
from core.exceptions import ConversationNotFoundError
from core.logging import get_logger
from core.models.conversation import (
    Citation,
    Conversation,
    Message,
    MessageRole,
    PinnedFact,
)

log = get_logger(__name__)

# Trigger summary update every N messages
_SUMMARY_INTERVAL = 10
# Number of recent messages to include in query context (2 exchanges)
_RECENT_MESSAGE_COUNT = 4


class ConversationContext(BaseModel):
    """Context assembled for a new query from conversation history."""

    summary: str | None = None
    recent_messages: list[Message] = Field(default_factory=list)
    pinned_facts: list[PinnedFact] = Field(default_factory=list)
    message_count: int = 0


class ConversationManager:
    """Manage conversation lifecycle, messaging, and context retrieval.

    Args:
        db: Database manager for SQLite operations.
        summariser: Conversation summariser for generating/updating summaries.
            May be None if summarisation is not available (e.g., no LLM).
    """

    def __init__(self, db: DatabaseManager, summariser: "ConversationSummariser | None" = None) -> None:
        self._db = db
        self._repo = ConversationRepository()
        self._summariser = summariser

    def create_conversation(self, project_id: UUID, title: str) -> Conversation:
        """Create a new conversation thread.

        Args:
            project_id: Parent project UUID.
            title: Conversation title.

        Returns:
            The created Conversation.
        """
        conn = self._db.get_connection()
        conv = self._repo.create(conn, project_id, title)
        log.info("conversation_created", id=str(conv.id), title=title)
        return conv

    def get_conversation(self, conversation_id: UUID) -> Conversation:
        """Retrieve a conversation with all messages and pinned facts.

        Args:
            conversation_id: Conversation UUID.

        Returns:
            Full Conversation including messages and pinned facts.

        Raises:
            ConversationNotFoundError: If the conversation does not exist.
        """
        conn = self._db.get_connection()
        conv = self._repo.get_by_id(conn, conversation_id)
        if conv is None:
            raise ConversationNotFoundError(
                f"Conversation not found: {conversation_id}",
                details={"conversation_id": str(conversation_id)},
            )
        return conv

    def list_conversations(self, project_id: UUID) -> list[dict]:
        """List all conversations for a project with metadata.

        Args:
            project_id: Project UUID.

        Returns:
            List of conversation dicts with id, title, summary, message_count,
            last_message_preview, created_at, updated_at, ordered by last_accessed desc.
        """
        conn = self._db.get_connection()
        convs = self._repo.list_by_project(conn, project_id)
        result = []
        for conv in convs:
            messages = self._repo.get_messages(conn, conv.id)
            last_preview = ""
            if messages:
                last_msg = messages[-1]
                last_preview = last_msg.content[:100]

            result.append({
                "id": str(conv.id),
                "title": conv.title,
                "summary": conv.summary,
                "message_count": len(messages),
                "last_message_preview": last_preview,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat(),
            })
        return result

    def add_message(
        self,
        conversation_id: UUID,
        role: MessageRole,
        content: str,
        citations: list[Citation] | None = None,
        confidence_score: float | None = None,
    ) -> Message:
        """Add a message to a conversation, triggering summary if needed.

        Args:
            conversation_id: Conversation UUID.
            role: Message sender role (USER, ASSISTANT).
            content: Message text.
            citations: Optional source citations (for assistant messages).
            confidence_score: Optional confidence score (for assistant messages).

        Returns:
            The created Message.
        """
        conn = self._db.get_connection()

        # Verify conversation exists
        conv = self._repo.get_by_id(conn, conversation_id)
        if conv is None:
            raise ConversationNotFoundError(
                f"Conversation not found: {conversation_id}",
            )

        msg = self._repo.add_message(
            conn, conversation_id, role, content, citations, confidence_score,
        )

        # Check if we should update the summary
        all_messages = self._repo.get_messages(conn, conversation_id)
        if len(all_messages) > 0 and len(all_messages) % _SUMMARY_INTERVAL == 0:
            self._update_summary(conversation_id, all_messages, conv.summary)

        log.info(
            "message_added",
            conversation_id=str(conversation_id),
            role=role.value,
            message_count=len(all_messages),
        )
        return msg

    def get_context_for_query(self, conversation_id: UUID) -> ConversationContext:
        """Build context for a new query from conversation history.

        This is a fast database-only operation (no LLM calls).
        Returns the pre-computed summary, last 4 messages, and all pinned facts.

        Args:
            conversation_id: Conversation UUID.

        Returns:
            ConversationContext with summary, recent messages, and pinned facts.

        Raises:
            ConversationNotFoundError: If the conversation does not exist.
        """
        conn = self._db.get_connection()
        conv = self._repo.get_by_id(conn, conversation_id)
        if conv is None:
            raise ConversationNotFoundError(
                f"Conversation not found: {conversation_id}",
            )

        all_messages = self._repo.get_messages(conn, conversation_id)
        recent = all_messages[-_RECENT_MESSAGE_COUNT:] if all_messages else []
        pinned = self._repo.get_pinned_facts(conn, conversation_id)

        return ConversationContext(
            summary=conv.summary,
            recent_messages=recent,
            pinned_facts=pinned,
            message_count=len(all_messages),
        )

    def delete_conversation(self, conversation_id: UUID) -> None:
        """Delete a conversation and all its data.

        Args:
            conversation_id: Conversation UUID.

        Raises:
            ConversationNotFoundError: If the conversation does not exist.
        """
        conn = self._db.get_connection()
        deleted = self._repo.delete(conn, conversation_id)
        if not deleted:
            raise ConversationNotFoundError(
                f"Conversation not found: {conversation_id}",
            )
        log.info("conversation_deleted", id=str(conversation_id))

    def update_summary(self, conversation_id: UUID) -> str | None:
        """Force a summary regeneration for a conversation.

        Args:
            conversation_id: Conversation UUID.

        Returns:
            The new summary text, or None if summarisation is unavailable.
        """
        conn = self._db.get_connection()
        conv = self._repo.get_by_id(conn, conversation_id)
        if conv is None:
            raise ConversationNotFoundError(
                f"Conversation not found: {conversation_id}",
            )
        messages = self._repo.get_messages(conn, conversation_id)
        return self._update_summary(conversation_id, messages, conv.summary)

    def _update_summary(
        self,
        conversation_id: UUID,
        messages: list[Message],
        existing_summary: str | None,
    ) -> str | None:
        """Generate or update the conversation summary via LLM.

        Returns:
            The new summary text, or None if summariser is unavailable.
        """
        if self._summariser is None or not messages:
            return None

        try:
            summary = self._summariser.summarise_conversation(messages, existing_summary)
            # Enforce 300-word limit
            words = summary.split()
            if len(words) > 300:
                summary = " ".join(words[:300]) + "..."

            conn = self._db.get_connection()
            self._repo.update_summary(conn, conversation_id, summary)
            log.info("summary_updated", conversation_id=str(conversation_id), words=len(summary.split()))
            return summary
        except Exception as e:
            log.warning("summary_update_failed", error=str(e))
            return None


# Avoid circular import — type is used in __init__ signature
from core.conversation.summariser import ConversationSummariser  # noqa: E402
