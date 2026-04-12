"""Proactive notification engine — alerts when new documents match user interests."""

from uuid import UUID

from core.database.connection import DatabaseManager
from core.logging import get_logger
from core.models.profile import ProactiveNotification, UserProfile
from core.vector_store.chroma_client import ChromaVectorStore

log = get_logger(__name__)


class ProactiveEngine:
    """Check for new documents relevant to the user's investigation focus.

    Args:
        db: Database manager.
        vector_store: ChromaDB for similarity search.
    """

    def __init__(self, db: DatabaseManager, vector_store: ChromaVectorStore) -> None:
        self._db = db
        self._vs = vector_store

    def check_for_relevant_updates(
        self, project_id: UUID, profile: UserProfile,
    ) -> list[ProactiveNotification]:
        """Check if recently ingested documents match the user's frequent topics.

        Args:
            project_id: Project UUID.
            profile: User's learned profile.

        Returns:
            List of notifications for relevant new content.
        """
        if not profile.frequent_topics:
            return []

        conn = self._db.get_connection()

        # Get recently imported documents (last 10)
        recent_docs = conn.execute(
            """SELECT id, filename FROM documents
               WHERE project_id = ? AND status = 'indexed'
               ORDER BY import_timestamp DESC LIMIT 10""",
            (str(project_id),),
        ).fetchall()

        if not recent_docs:
            return []

        # Get recent chunk content for topic matching
        notifications: list[ProactiveNotification] = []
        seen_docs: set[str] = set()

        for doc in recent_docs:
            doc_id = doc["id"]
            if doc_id in seen_docs:
                continue

            # Get first few chunks of this document
            chunks = conn.execute(
                "SELECT content FROM chunks WHERE document_id = ? LIMIT 3",
                (doc_id,),
            ).fetchall()

            if not chunks:
                continue

            combined = " ".join(c["content"].lower() for c in chunks)

            # Check against frequent topics
            for topic in profile.frequent_topics[:5]:
                if topic.lower() in combined:
                    seen_docs.add(doc_id)
                    notifications.append(ProactiveNotification(
                        message=f"New document '{doc['filename']}' contains information about '{topic}' which you've been investigating.",
                        topic=topic,
                        document_id=UUID(doc_id),
                        document_name=doc["filename"],
                        relevance_score=0.8,
                    ))
                    break  # One notification per document

        log.info(
            "proactive_check_complete",
            project_id=str(project_id),
            notifications=len(notifications),
        )
        return notifications
