"""FastAPI dependency injection providers.

These functions are used with FastAPI's Depends() to inject shared
instances of database, vector store, LLM client, and settings.
"""

from functools import lru_cache
from pathlib import Path

from backend.config import Settings, get_settings
from core.database.connection import DatabaseManager
from core.rag.llm_client import OllamaClient
from core.vector_store.chroma_client import ChromaVectorStore

# Module-level singletons — initialised on first use
_db_manager: DatabaseManager | None = None
_vector_store: ChromaVectorStore | None = None
_ollama_client: OllamaClient | None = None


def get_db() -> DatabaseManager:
    """Provide the singleton DatabaseManager instance.

    Returns:
        Initialized DatabaseManager.
    """
    global _db_manager
    if _db_manager is None:
        settings = get_settings()
        _db_manager = DatabaseManager(db_path=settings.sqlite_file)
        _db_manager.initialize()
    return _db_manager


def get_vector_store() -> ChromaVectorStore:
    """Provide the singleton ChromaVectorStore instance.

    Returns:
        Initialized ChromaVectorStore.
    """
    global _vector_store
    if _vector_store is None:
        settings = get_settings()
        _vector_store = ChromaVectorStore(persist_directory=settings.chroma_dir)
    return _vector_store


def get_ollama_client() -> OllamaClient:
    """Provide the singleton OllamaClient instance.

    Returns:
        Configured OllamaClient.
    """
    global _ollama_client
    if _ollama_client is None:
        settings = get_settings()
        _ollama_client = OllamaClient(
            base_url=settings.ollama_base_url,
            model_name=settings.ollama_model,
            embed_model_name=settings.ollama_embed_model,
        )
    return _ollama_client


@lru_cache(maxsize=1)
def get_app_settings() -> Settings:
    """Provide cached Settings for route injection.

    Returns:
        Application settings.
    """
    return get_settings()
