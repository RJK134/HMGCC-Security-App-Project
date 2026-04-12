"""Repository for document CRUD operations."""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4

from core.models.document import (
    DocumentMetadata,
    DocumentStatus,
    DocumentType,
    SourceTier,
)


class DocumentRepository:
    """Data access layer for documents."""

    def create(
        self,
        conn: sqlite3.Connection,
        project_id: UUID,
        filename: str,
        filepath: Path,
        filetype: DocumentType,
        size_bytes: int,
        source_tier: SourceTier = SourceTier.TIER_4_UNVERIFIED,
        page_count: int | None = None,
        metadata: dict | None = None,
    ) -> DocumentMetadata:
        """Create a new document record.

        Args:
            conn: SQLite connection.
            project_id: Parent project UUID.
            filename: Original filename.
            filepath: Path where the file is stored.
            filetype: Detected document type.
            size_bytes: File size in bytes.
            source_tier: Quality tier classification.
            page_count: Number of pages (for PDFs).
            metadata: Additional metadata dict.

        Returns:
            The created DocumentMetadata.
        """
        doc_id = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()
        meta_json = json.dumps(metadata or {})

        conn.execute(
            "INSERT INTO documents "
            "(id, project_id, filename, filepath, filetype, size_bytes, status, "
            "source_tier, import_timestamp, page_count, metadata_json) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                doc_id, str(project_id), filename, str(filepath), filetype.value,
                size_bytes, DocumentStatus.PENDING.value, source_tier.value,
                now, page_count, meta_json,
            ),
        )
        conn.commit()
        return DocumentMetadata(
            id=UUID(doc_id),
            project_id=project_id,
            filename=filename,
            filepath=filepath,
            filetype=filetype,
            size_bytes=size_bytes,
            status=DocumentStatus.PENDING,
            source_tier=source_tier,
            import_timestamp=datetime.fromisoformat(now),
            page_count=page_count,
            metadata=metadata or {},
        )

    def get_by_id(self, conn: sqlite3.Connection, document_id: UUID) -> DocumentMetadata | None:
        """Get a document by ID.

        Args:
            conn: SQLite connection.
            document_id: Document UUID.

        Returns:
            DocumentMetadata if found, None otherwise.
        """
        row = conn.execute("SELECT * FROM documents WHERE id = ?", (str(document_id),)).fetchone()
        if row is None:
            return None
        return self._row_to_model(row)

    def list_by_project(self, conn: sqlite3.Connection, project_id: UUID) -> list[DocumentMetadata]:
        """List all documents for a project.

        Args:
            conn: SQLite connection.
            project_id: Project UUID.

        Returns:
            List of documents ordered by import timestamp descending.
        """
        rows = conn.execute(
            "SELECT * FROM documents WHERE project_id = ? ORDER BY import_timestamp DESC",
            (str(project_id),),
        ).fetchall()
        return [self._row_to_model(row) for row in rows]

    def update_status(
        self, conn: sqlite3.Connection, document_id: UUID, status: DocumentStatus
    ) -> bool:
        """Update a document's processing status.

        Args:
            conn: SQLite connection.
            document_id: Document UUID.
            status: New status.

        Returns:
            True if updated, False if not found.
        """
        cursor = conn.execute(
            "UPDATE documents SET status = ? WHERE id = ?",
            (status.value, str(document_id)),
        )
        conn.commit()
        return cursor.rowcount > 0

    def update_tier(
        self, conn: sqlite3.Connection, document_id: UUID, tier: SourceTier
    ) -> bool:
        """Update a document's source quality tier.

        Args:
            conn: SQLite connection.
            document_id: Document UUID.
            tier: New source tier.

        Returns:
            True if updated, False if not found.
        """
        now = datetime.now(timezone.utc).isoformat()
        cursor = conn.execute(
            "UPDATE documents SET source_tier = ? WHERE id = ?",
            (tier.value, str(document_id)),
        )
        # Also update the source_tiers tracking table
        conn.execute(
            "INSERT OR REPLACE INTO source_tiers (document_id, tier, assigned_by, assigned_at) "
            "VALUES (?, ?, 'user', ?)",
            (str(document_id), tier.value, now),
        )
        conn.commit()
        return cursor.rowcount > 0

    def delete(self, conn: sqlite3.Connection, document_id: UUID) -> bool:
        """Delete a document and its chunks (cascading).

        Args:
            conn: SQLite connection.
            document_id: Document UUID.

        Returns:
            True if deleted, False if not found.
        """
        cursor = conn.execute("DELETE FROM documents WHERE id = ?", (str(document_id),))
        conn.commit()
        return cursor.rowcount > 0

    def count_by_project(self, conn: sqlite3.Connection, project_id: UUID) -> int:
        """Count documents in a project.

        Args:
            conn: SQLite connection.
            project_id: Project UUID.

        Returns:
            Number of documents.
        """
        row = conn.execute(
            "SELECT COUNT(*) FROM documents WHERE project_id = ?", (str(project_id),)
        ).fetchone()
        return row[0]

    def _row_to_model(self, row: sqlite3.Row) -> DocumentMetadata:
        """Convert a database row to a DocumentMetadata model."""
        return DocumentMetadata(
            id=UUID(row["id"]),
            project_id=UUID(row["project_id"]),
            filename=row["filename"],
            filepath=Path(row["filepath"]),
            filetype=DocumentType(row["filetype"]),
            size_bytes=row["size_bytes"],
            status=DocumentStatus(row["status"]),
            source_tier=SourceTier(row["source_tier"]),
            import_timestamp=datetime.fromisoformat(row["import_timestamp"]),
            page_count=row["page_count"],
            metadata=json.loads(row["metadata_json"]) if row["metadata_json"] else {},
        )
