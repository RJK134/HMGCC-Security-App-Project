"""Vector similarity search using ChromaDB embeddings."""

from uuid import UUID

from core.ingest.embedder import Embedder
from core.logging import get_logger
from core.rag.search_models import SearchResult
from core.vector_store.chroma_client import ChromaVectorStore

log = get_logger(__name__)


class VectorSearcher:
    """Semantic search over document embeddings via ChromaDB.

    Args:
        vector_store: ChromaDB wrapper.
        embedder: Embedding generator (same model used at ingest time).
    """

    def __init__(self, vector_store: ChromaVectorStore, embedder: Embedder) -> None:
        self._store = vector_store
        self._embedder = embedder

    def search(
        self,
        query: str,
        project_id: UUID,
        top_k: int = 20,
        filters: dict | None = None,
    ) -> list[SearchResult]:
        """Embed the query and search ChromaDB for similar chunks.

        Args:
            query: Natural-language query text.
            project_id: Project UUID to search within.
            top_k: Maximum results to return.
            filters: Optional ChromaDB where-filter dict.

        Returns:
            Ranked list of SearchResult with similarity scores in [0, 1].
        """
        try:
            query_embedding = self._embedder._client.generate_embedding(query)
        except Exception as e:
            log.error("vector_search_embed_failed", error=str(e))
            return []

        try:
            raw = self._store.query(
                project_id=project_id,
                query_embedding=query_embedding,
                n_results=top_k,
                where_filter=filters,
            )
        except Exception as e:
            log.error("vector_search_query_failed", error=str(e))
            return []

        results: list[SearchResult] = []
        if not raw or not raw.get("ids") or not raw["ids"][0]:
            return results

        ids = raw["ids"][0]
        documents = raw["documents"][0] if raw.get("documents") else [""] * len(ids)
        distances = raw["distances"][0] if raw.get("distances") else [0.0] * len(ids)
        metadatas = raw["metadatas"][0] if raw.get("metadatas") else [{}] * len(ids)

        for chunk_id, doc, dist, meta in zip(ids, documents, distances, metadatas):
            # ChromaDB returns L2 distance by default; convert to similarity
            score = 1.0 / (1.0 + dist)
            results.append(SearchResult(
                chunk_id=chunk_id,
                content=doc,
                score=score,
                metadata=meta,
            ))

        log.info("vector_search_complete", project_id=str(project_id), results=len(results))
        return results
