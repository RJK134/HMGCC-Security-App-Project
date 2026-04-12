"""Document upload, listing, and management API endpoints."""

import shutil
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile
from pydantic import BaseModel

from backend.config import Settings
from backend.dependencies import get_app_settings, get_db, get_ollama_client, get_vector_store
from core.database.connection import DatabaseManager
from core.database.repositories.document_repo import DocumentRepository
from core.exceptions import DocumentProcessingError, ProjectNotFoundError
from core.ingest.embedder import Embedder
from core.ingest.pipeline import IngestionPipeline
from core.logging import get_logger
from core.models.document import DocumentMetadata, DocumentStatus, SourceTier
from core.rag.llm_client import OllamaClient
from core.vector_store.chroma_client import ChromaVectorStore

log = get_logger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])


# --- Request/Response schemas ---

class BatchImportRequest(BaseModel):
    directory_path: str
    project_id: UUID
    recursive: bool = True
    source_tier: SourceTier = SourceTier.TIER_4_UNVERIFIED


class TierUpdateRequest(BaseModel):
    tier: SourceTier


class DocumentDetail(BaseModel):
    document: DocumentMetadata
    chunk_count: int
    sample_chunks: list[dict]

    model_config = {"arbitrary_types_allowed": True}


# --- Helper ---

def _get_pipeline(
    db: DatabaseManager,
    vector_store: ChromaVectorStore,
    ollama: OllamaClient,
    settings: Settings,
) -> IngestionPipeline:
    embedder = Embedder(ollama)
    return IngestionPipeline(db, vector_store, embedder, settings)


# --- Endpoints ---

@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    project_id: UUID = Form(...),
    source_tier: SourceTier = Form(SourceTier.TIER_4_UNVERIFIED),
    db: DatabaseManager = Depends(get_db),
    vector_store: ChromaVectorStore = Depends(get_vector_store),
    ollama: OllamaClient = Depends(get_ollama_client),
    settings: Settings = Depends(get_app_settings),
) -> dict:
    """Upload and ingest a single document.

    Saves the file locally, then runs it through the full ingestion pipeline.
    """
    # Save uploaded file
    upload_dir = Path(settings.chroma_path).parent.parent / "uploads" / str(project_id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    dest = upload_dir / (file.filename or "unnamed")

    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    log.info("file_uploaded", filename=file.filename, dest=str(dest))

    pipeline = _get_pipeline(db, vector_store, ollama, settings)
    doc = pipeline.ingest_file(dest, project_id, source_tier)

    return {"status": "ok", "document": doc.model_dump(mode="json")}


@router.post("/batch")
def batch_import(
    request: BatchImportRequest,
    db: DatabaseManager = Depends(get_db),
    vector_store: ChromaVectorStore = Depends(get_vector_store),
    ollama: OllamaClient = Depends(get_ollama_client),
    settings: Settings = Depends(get_app_settings),
) -> dict:
    """Batch import all supported files from a directory."""
    dir_path = Path(request.directory_path)
    if not dir_path.is_dir():
        raise DocumentProcessingError(
            f"Directory not found: {request.directory_path}",
            details={"path": request.directory_path},
        )

    pipeline = _get_pipeline(db, vector_store, ollama, settings)
    results = pipeline.ingest_directory(
        dir_path, request.project_id, request.recursive, request.source_tier,
    )

    succeeded = sum(1 for d in results if d.status == DocumentStatus.INDEXED)
    failed = sum(1 for d in results if d.status == DocumentStatus.FAILED)

    return {
        "status": "ok",
        "total": len(results),
        "succeeded": succeeded,
        "failed": failed,
        "documents": [d.model_dump(mode="json") for d in results],
    }


@router.get("")
def list_documents(
    project_id: UUID,
    limit: int = 50,
    offset: int = 0,
    db: DatabaseManager = Depends(get_db),
) -> dict:
    """List documents for a project with pagination."""
    doc_repo = DocumentRepository()
    conn = db.get_connection()
    docs = doc_repo.list_by_project(conn, project_id)

    # Apply pagination
    paginated = docs[offset : offset + limit]
    return {
        "total": len(docs),
        "limit": limit,
        "offset": offset,
        "documents": [d.model_dump(mode="json") for d in paginated],
    }


@router.get("/{document_id}")
def get_document(
    document_id: UUID,
    db: DatabaseManager = Depends(get_db),
) -> dict:
    """Get document detail including chunk count and sample chunks."""
    doc_repo = DocumentRepository()
    conn = db.get_connection()
    doc = doc_repo.get_by_id(conn, document_id)

    if doc is None:
        raise DocumentProcessingError(
            f"Document not found: {document_id}",
            details={"document_id": str(document_id)},
        )

    # Get chunk count and samples
    chunk_count = conn.execute(
        "SELECT COUNT(*) FROM chunks WHERE document_id = ?", (str(document_id),)
    ).fetchone()[0]

    sample_rows = conn.execute(
        "SELECT chunk_index, page_number, section_heading, token_count, "
        "substr(content, 1, 200) as preview FROM chunks "
        "WHERE document_id = ? ORDER BY chunk_index LIMIT 5",
        (str(document_id),),
    ).fetchall()

    samples = [
        {
            "chunk_index": r["chunk_index"],
            "page_number": r["page_number"],
            "section_heading": r["section_heading"],
            "token_count": r["token_count"],
            "preview": r["preview"],
        }
        for r in sample_rows
    ]

    return {
        "document": doc.model_dump(mode="json"),
        "chunk_count": chunk_count,
        "sample_chunks": samples,
    }


@router.delete("/{document_id}")
def delete_document(
    document_id: UUID,
    db: DatabaseManager = Depends(get_db),
    vector_store: ChromaVectorStore = Depends(get_vector_store),
) -> dict:
    """Delete a document, its chunks from SQLite, and vectors from ChromaDB."""
    doc_repo = DocumentRepository()
    conn = db.get_connection()
    doc = doc_repo.get_by_id(conn, document_id)

    if doc is None:
        raise DocumentProcessingError(
            f"Document not found: {document_id}",
            details={"document_id": str(document_id)},
        )

    # Remove from ChromaDB
    try:
        vector_store.delete_by_document(doc.project_id, document_id)
    except Exception as e:
        log.warning("chroma_delete_failed", error=str(e))

    # Remove from SQLite (cascades to chunks)
    doc_repo.delete(conn, document_id)

    log.info("document_deleted", document_id=str(document_id))
    return {"status": "ok", "document_id": str(document_id)}


@router.patch("/{document_id}/tier")
def update_document_tier(
    document_id: UUID,
    request: TierUpdateRequest,
    db: DatabaseManager = Depends(get_db),
) -> dict:
    """Update the source quality tier of a document."""
    doc_repo = DocumentRepository()
    conn = db.get_connection()

    if not doc_repo.update_tier(conn, document_id, request.tier):
        raise DocumentProcessingError(
            f"Document not found: {document_id}",
            details={"document_id": str(document_id)},
        )

    doc = doc_repo.get_by_id(conn, document_id)
    return {"status": "ok", "document": doc.model_dump(mode="json") if doc else None}
