"""Health check endpoint — reports system status."""

from fastapi import APIRouter, Depends

from backend.dependencies import get_db, get_ollama_client, get_vector_store
from backend.schemas.responses import HealthResponse
from core.database.connection import DatabaseManager
from core.rag.llm_client import OllamaClient
from core.vector_store.chroma_client import ChromaVectorStore

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check(
    db: DatabaseManager = Depends(get_db),
    vector_store: ChromaVectorStore = Depends(get_vector_store),
    ollama: OllamaClient = Depends(get_ollama_client),
) -> HealthResponse:
    """Return current system status including connectivity to all services.

    Args:
        db: Database manager instance.
        vector_store: ChromaDB vector store instance.
        ollama: Ollama LLM client instance.

    Returns:
        HealthResponse with status of all subsystems.
    """
    # Check Ollama
    ollama_ok = ollama.health_check()
    models: list[str] = []
    if ollama_ok:
        try:
            models = ollama.list_models()
        except Exception:
            pass

    # Check database
    db_ok = False
    doc_count = 0
    try:
        conn = db.get_connection()
        conn.execute("SELECT 1")
        row = conn.execute("SELECT COUNT(*) FROM documents").fetchone()
        doc_count = row[0] if row else 0
        db_ok = True
    except Exception:
        pass

    # Check vector store
    vs_ok = vector_store.heartbeat()

    # Determine overall status
    if db_ok and vs_ok and ollama_ok:
        status = "ok"
    elif db_ok and vs_ok:
        status = "degraded"  # Ollama not running, but core storage works
    else:
        status = "error"

    return HealthResponse(
        status=status,
        ollama_connected=ollama_ok,
        available_models=models,
        database_ok=db_ok,
        vector_store_ok=vs_ok,
        document_count=doc_count,
    )
