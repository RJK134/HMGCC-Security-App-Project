"""Repository for conversation and message CRUD operations."""

import json
import sqlite3
from datetime import datetime, timezone
from uuid import UUID, uuid4

from core.models.conversation import (
    Citation,
    Conversation,
    Message,
    MessageRole,
    PinnedFact,
)


class ConversationRepository:
    """Data access layer for conversations, messages, and pinned facts."""

    def create(
        self, conn: sqlite3.Connection, project_id: UUID, title: str
    ) -> Conversation:
        """Create a new conversation.

        Args:
            conn: SQLite connection.
            project_id: Parent project UUID.
            title: Conversation title.

        Returns:
            The created Conversation.
        """
        conv_id = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()
        conn.execute(
            "INSERT INTO conversations (id, project_id, title, created_at, updated_at, last_accessed) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (conv_id, str(project_id), title, now, now, now),
        )
        conn.commit()
        return Conversation(
            id=UUID(conv_id),
            project_id=project_id,
            title=title,
            created_at=datetime.fromisoformat(now),
            updated_at=datetime.fromisoformat(now),
        )

    def get_by_id(self, conn: sqlite3.Connection, conversation_id: UUID) -> Conversation | None:
        """Get a conversation by ID including its messages and pinned facts.

        Args:
            conn: SQLite connection.
            conversation_id: Conversation UUID.

        Returns:
            Conversation with messages and pinned facts, or None if not found.
        """
        row = conn.execute(
            "SELECT * FROM conversations WHERE id = ?", (str(conversation_id),)
        ).fetchone()
        if row is None:
            return None

        messages = self.get_messages(conn, conversation_id)
        pinned = self.get_pinned_facts(conn, conversation_id)

        return Conversation(
            id=UUID(row["id"]),
            project_id=UUID(row["project_id"]),
            title=row["title"],
            summary=row["summary"],
            messages=messages,
            pinned_facts=pinned,
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def list_by_project(self, conn: sqlite3.Connection, project_id: UUID) -> list[Conversation]:
        """List all conversations for a project (without messages for performance).

        Args:
            conn: SQLite connection.
            project_id: Project UUID.

        Returns:
            List of conversations ordered by updated_at descending.
        """
        rows = conn.execute(
            "SELECT * FROM conversations WHERE project_id = ? ORDER BY updated_at DESC",
            (str(project_id),),
        ).fetchall()
        return [
            Conversation(
                id=UUID(row["id"]),
                project_id=UUID(row["project_id"]),
                title=row["title"],
                summary=row["summary"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )
            for row in rows
        ]

    def add_message(
        self,
        conn: sqlite3.Connection,
        conversation_id: UUID,
        role: MessageRole,
        content: str,
        citations: list[Citation] | None = None,
        confidence_score: float | None = None,
    ) -> Message:
        """Add a message to a conversation.

        Args:
            conn: SQLite connection.
            conversation_id: Conversation UUID.
            role: Message sender role.
            content: Message text content.
            citations: Optional list of source citations.
            confidence_score: Optional confidence score for assistant messages.

        Returns:
            The created Message.
        """
        msg_id = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()
        citations_json = json.dumps([c.model_dump(mode="json") for c in (citations or [])])

        conn.execute(
            "INSERT INTO messages (id, conversation_id, role, content, citations_json, "
            "confidence_score, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (msg_id, str(conversation_id), role.value, content, citations_json,
             confidence_score, now),
        )
        # Update conversation's updated_at
        conn.execute(
            "UPDATE conversations SET updated_at = ?, last_accessed = ? WHERE id = ?",
            (now, now, str(conversation_id)),
        )
        conn.commit()

        return Message(
            id=UUID(msg_id),
            conversation_id=conversation_id,
            role=role,
            content=content,
            citations=citations or [],
            confidence_score=confidence_score,
            created_at=datetime.fromisoformat(now),
        )

    def get_messages(
        self, conn: sqlite3.Connection, conversation_id: UUID
    ) -> list[Message]:
        """Get all messages for a conversation.

        Args:
            conn: SQLite connection.
            conversation_id: Conversation UUID.

        Returns:
            List of messages ordered by creation time.
        """
        rows = conn.execute(
            "SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at",
            (str(conversation_id),),
        ).fetchall()
        return [self._row_to_message(row) for row in rows]

    def update_summary(
        self, conn: sqlite3.Connection, conversation_id: UUID, summary: str
    ) -> bool:
        """Update a conversation's summary text.

        Args:
            conn: SQLite connection.
            conversation_id: Conversation UUID.
            summary: New summary text.

        Returns:
            True if updated, False if not found.
        """
        now = datetime.now(timezone.utc).isoformat()
        cursor = conn.execute(
            "UPDATE conversations SET summary = ?, updated_at = ? WHERE id = ?",
            (summary, now, str(conversation_id)),
        )
        conn.commit()
        return cursor.rowcount > 0

    def delete(self, conn: sqlite3.Connection, conversation_id: UUID) -> bool:
        """Delete a conversation and all its messages and pinned facts (cascading).

        Args:
            conn: SQLite connection.
            conversation_id: Conversation UUID.

        Returns:
            True if deleted, False if not found.
        """
        cursor = conn.execute(
            "DELETE FROM conversations WHERE id = ?", (str(conversation_id),)
        )
        conn.commit()
        return cursor.rowcount > 0

    def add_pinned_fact(
        self,
        conn: sqlite3.Connection,
        conversation_id: UUID,
        content: str,
        source_refs: list[Citation] | None = None,
    ) -> PinnedFact:
        """Pin a key finding to a conversation.

        Args:
            conn: SQLite connection.
            conversation_id: Conversation UUID.
            content: The fact text to pin.
            source_refs: Optional source citations supporting the fact.

        Returns:
            The created PinnedFact.
        """
        fact_id = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()
        refs_json = json.dumps([c.model_dump(mode="json") for c in (source_refs or [])])

        conn.execute(
            "INSERT INTO pinned_facts (id, conversation_id, content, source_refs_json, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (fact_id, str(conversation_id), content, refs_json, now),
        )
        conn.commit()
        return PinnedFact(
            id=UUID(fact_id),
            conversation_id=conversation_id,
            content=content,
            source_refs=source_refs or [],
            created_at=datetime.fromisoformat(now),
        )

    def get_pinned_facts(
        self, conn: sqlite3.Connection, conversation_id: UUID
    ) -> list[PinnedFact]:
        """Get all pinned facts for a conversation.

        Args:
            conn: SQLite connection.
            conversation_id: Conversation UUID.

        Returns:
            List of pinned facts ordered by creation time.
        """
        rows = conn.execute(
            "SELECT * FROM pinned_facts WHERE conversation_id = ? ORDER BY created_at",
            (str(conversation_id),),
        ).fetchall()
        return [
            PinnedFact(
                id=UUID(row["id"]),
                conversation_id=UUID(row["conversation_id"]),
                content=row["content"],
                source_refs=[
                    Citation(**c) for c in json.loads(row["source_refs_json"] or "[]")
                ],
                created_at=datetime.fromisoformat(row["created_at"]),
            )
            for row in rows
        ]

    def _row_to_message(self, row: sqlite3.Row) -> Message:
        """Convert a database row to a Message model."""
        return Message(
            id=UUID(row["id"]),
            conversation_id=UUID(row["conversation_id"]),
            role=MessageRole(row["role"]),
            content=row["content"],
            citations=[
                Citation(**c) for c in json.loads(row["citations_json"] or "[]")
            ],
            confidence_score=row["confidence_score"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )
