"""Repair missing filename metadata in ChromaDB chunks.

Documents imported before the filename metadata fix have chunks without
the 'filename' field in their ChromaDB metadata, causing citations to
show 'unknown'. This module backfills filenames from the SQLite document
table into ChromaDB chunk metadata.
"""

from uuid import UUID

from core.database.connection import DatabaseManager
from core.logging import get_logger
from core.vector_store.chroma_client import ChromaVectorStore

log = get_logger(__name__)


def repair_missing_filenames(db: DatabaseManager, vector_store: ChromaVectorStore) -> int:
    """Backfill missing 'filename' metadata in ChromaDB chunks from SQLite.

    Iterates all projects, checks each chunk's metadata for a 'filename'
    field, and fills it from the SQLite documents table if missing.
    This operation is idempotent — chunks that already have filenames are skipped.

    Args:
        db: Database manager for reading document filenames.
        vector_store: ChromaDB wrapper for updating chunk metadata.

    Returns:
        Total number of chunks repaired across all projects.
    """
    conn = db.get_connection()
    total_repaired = 0

    # Get all projects
    try:
        projects = conn.execute("SELECT id FROM projects").fetchall()
    except Exception:
        return 0

    # Build a global document_id → filename lookup
    doc_rows = conn.execute("SELECT id, filename FROM documents").fetchall()
    doc_filenames = {row["id"]: row["filename"] for row in doc_rows}

    if not doc_filenames:
        return 0

    for project in projects:
        project_id = UUID(project["id"])
        try:
            collection = vector_store.get_or_create_collection(project_id)
            results = collection.get(include=["metadatas"])

            if not results or not results.get("ids"):
                continue

            for i, meta in enumerate(results["metadatas"]):
                if not meta:
                    continue
                if meta.get("filename"):
                    continue  # Already has filename — skip

                doc_id = meta.get("document_id", "")
                if doc_id in doc_filenames:
                    meta["filename"] = doc_filenames[doc_id]
                    collection.update(
                        ids=[results["ids"][i]],
                        metadatas=[meta],
                    )
                    total_repaired += 1

        except Exception as e:
            log.warning(
                "metadata_repair_project_failed",
                project_id=str(project_id),
                error=str(e),
            )
            continue

    if total_repaired > 0:
        log.info("metadata_repair_complete", chunks_repaired=total_repaired)
    else:
        log.info("metadata_repair_complete", message="All chunks already have filenames")

    return total_repaired
