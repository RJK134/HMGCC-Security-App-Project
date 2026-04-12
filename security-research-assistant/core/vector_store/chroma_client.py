"""ChromaDB wrapper with collection management for per-project vector storage."""

from pathlib import Path
from uuid import UUID

import chromadb

from core.exceptions import VectorStoreError
from core.logging import get_logger

log = get_logger(__name__)


class ChromaVectorStore:
    """Manages ChromaDB collections and vector operations.

    Each project gets its own collection named ``project_{id}_chunks``.

    Args:
        persist_directory: Path to the ChromaDB persistent storage directory.
    """

    def __init__(self, persist_directory: Path) -> None:
        self._persist_dir = persist_directory
        self._persist_dir.mkdir(parents=True, exist_ok=True)
        try:
            self._client = chromadb.PersistentClient(path=str(self._persist_dir))
            log.info("chroma_initialized", path=str(self._persist_dir))
        except Exception as e:
            raise VectorStoreError(f"Failed to initialize ChromaDB: {e}") from e

    def _collection_name(self, project_id: UUID) -> str:
        """Build the collection name for a project."""
        return f"project_{project_id}_chunks"

    def get_or_create_collection(self, project_id: UUID) -> chromadb.Collection:
        """Get or create a ChromaDB collection for a project.

        Args:
            project_id: Project UUID.

        Returns:
            The ChromaDB collection.

        Raises:
            VectorStoreError: If collection creation fails.
        """
        name = self._collection_name(project_id)
        try:
            collection = self._client.get_or_create_collection(
                name=name,
                metadata={"project_id": str(project_id)},
            )
            log.debug("chroma_collection_ready", collection=name)
            return collection
        except Exception as e:
            raise VectorStoreError(
                f"Failed to get/create collection '{name}': {e}"
            ) from e

    def add_chunks(
        self,
        project_id: UUID,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict],
    ) -> None:
        """Add document chunks with embeddings to a project collection.

        Args:
            project_id: Project UUID.
            ids: Unique chunk IDs.
            embeddings: Embedding vectors for each chunk.
            documents: Text content of each chunk.
            metadatas: Metadata dicts for each chunk.

        Raises:
            VectorStoreError: If the add operation fails.
        """
        collection = self.get_or_create_collection(project_id)
        try:
            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
            )
            log.info("chroma_chunks_added", project_id=str(project_id), count=len(ids))
        except Exception as e:
            raise VectorStoreError(f"Failed to add chunks: {e}") from e

    def query(
        self,
        project_id: UUID,
        query_embedding: list[float],
        n_results: int = 10,
        where_filter: dict | None = None,
    ) -> dict:
        """Query a project collection for similar chunks.

        Args:
            project_id: Project UUID.
            query_embedding: Query vector.
            n_results: Maximum number of results.
            where_filter: Optional metadata filter.

        Returns:
            ChromaDB query results dict with ids, documents, distances, metadatas.

        Raises:
            VectorStoreError: If the query fails.
        """
        collection = self.get_or_create_collection(project_id)
        try:
            kwargs: dict = {
                "query_embeddings": [query_embedding],
                "n_results": n_results,
            }
            if where_filter:
                kwargs["where"] = where_filter
            results = collection.query(**kwargs)
            return results
        except Exception as e:
            raise VectorStoreError(f"Failed to query collection: {e}") from e

    def delete_by_document(self, project_id: UUID, document_id: UUID) -> None:
        """Remove all chunks belonging to a specific document.

        Args:
            project_id: Project UUID.
            document_id: Document UUID whose chunks should be removed.

        Raises:
            VectorStoreError: If the delete operation fails.
        """
        collection = self.get_or_create_collection(project_id)
        try:
            collection.delete(where={"document_id": str(document_id)})
            log.info(
                "chroma_document_deleted",
                project_id=str(project_id),
                document_id=str(document_id),
            )
        except Exception as e:
            raise VectorStoreError(f"Failed to delete document chunks: {e}") from e

    def delete_collection(self, project_id: UUID) -> None:
        """Delete an entire project collection.

        Args:
            project_id: Project UUID whose collection should be removed.

        Raises:
            VectorStoreError: If the delete operation fails.
        """
        name = self._collection_name(project_id)
        try:
            self._client.delete_collection(name=name)
            log.info("chroma_collection_deleted", collection=name)
        except Exception as e:
            raise VectorStoreError(f"Failed to delete collection '{name}': {e}") from e

    def count(self, project_id: UUID) -> int:
        """Count chunks stored for a project.

        Args:
            project_id: Project UUID.

        Returns:
            Number of chunks in the project's collection.
        """
        collection = self.get_or_create_collection(project_id)
        return collection.count()

    def heartbeat(self) -> bool:
        """Check if ChromaDB is responsive.

        Returns:
            True if ChromaDB responds to a heartbeat.
        """
        try:
            self._client.heartbeat()
            return True
        except Exception:
            return False
