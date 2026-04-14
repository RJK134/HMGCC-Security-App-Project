"""Data maintenance API — export, import, version, and stats."""

import tempfile
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import FileResponse

from backend.config import Settings
from backend.dependencies import get_app_settings, get_db, get_vector_store
from core.database.connection import DatabaseManager
from core.logging import get_logger
from core.vector_store.chroma_client import ChromaVectorStore

log = get_logger(__name__)
router = APIRouter(prefix="/maintenance", tags=["maintenance"])

VERSION = "0.1.0"


def _get_updater(settings: Settings):
    from scripts.update import SRAUpdater
    return SRAUpdater(Path(settings.chroma_path).parent)


@router.get("/version")
def get_version(settings: Settings = Depends(get_app_settings)) -> dict:
    """Return current version and data statistics."""
    updater = _get_updater(settings)
    stats = updater.get_data_stats()
    return {"version": VERSION, "stats": stats}


@router.post("/export")
def export_data(settings: Settings = Depends(get_app_settings)):
    """Export all user data as a downloadable .sra-backup file."""
    updater = _get_updater(settings)
    tmp = Path(tempfile.mkdtemp()) / "sra-export"
    archive = updater.export_data(tmp)
    return FileResponse(
        str(archive),
        media_type="application/zip",
        filename="sra-data-export.sra-backup",
    )


@router.post("/import")
async def import_data(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_app_settings),
) -> dict:
    """Import data from a .sra-backup file."""
    tmp = Path(tempfile.mkdtemp()) / (file.filename or "import.sra-backup")
    with open(tmp, "wb") as f:
        content = await file.read()
        f.write(content)

    updater = _get_updater(settings)
    stats = updater.import_data(tmp)
    return {"status": "ok", "stats": stats}


@router.post("/reindex-metadata/{project_id}")
def reindex_metadata(
    project_id: UUID,
    db: DatabaseManager = Depends(get_db),
    vector_store: ChromaVectorStore = Depends(get_vector_store),
) -> dict:
    """Re-index document metadata in ChromaDB for chunks missing filename.

    Documents imported before the filename metadata fix will have chunks
    without filename in their ChromaDB metadata. This endpoint backfills
    filenames from the SQLite document table.
    """
    conn = db.get_connection()

    # Get all documents for project
    docs = conn.execute(
        "SELECT id, filename FROM documents WHERE project_id = ?",
        (str(project_id),),
    ).fetchall()
    doc_filenames = {row["id"]: row["filename"] for row in docs}

    if not doc_filenames:
        return {"status": "ok", "updated_chunks": 0, "message": "No documents found."}

    collection = vector_store.get_or_create_collection(project_id)
    results = collection.get(include=["metadatas"])

    updated = 0
    for i, meta in enumerate(results["metadatas"]):
        if not meta.get("filename"):
            doc_id = meta.get("document_id", "")
            if doc_id in doc_filenames:
                meta["filename"] = doc_filenames[doc_id]
                collection.update(
                    ids=[results["ids"][i]],
                    metadatas=[meta],
                )
                updated += 1

    log.info(
        "metadata_reindexed",
        project_id=str(project_id),
        total_chunks=len(results["ids"]),
        updated=updated,
    )
    return {"status": "ok", "updated_chunks": updated, "total_chunks": len(results["ids"])}
