"""BM25 keyword search over document chunks stored in SQLite."""

from uuid import UUID

from rank_bm25 import BM25Okapi

from core.database.connection import DatabaseManager
from core.logging import get_logger
from core.rag.search_models import SearchResult

log = get_logger(__name__)


def _tokenize(text: str) -> list[str]:
    """Simple whitespace + lowercase tokenizer."""
    return text.lower().split()


class KeywordSearcher:
    """BM25 keyword search with per-project index caching.

    Args:
        db: Database manager for reading chunks from SQLite.
    """

    def __init__(self, db: DatabaseManager) -> None:
        self._db = db
        self._cache: dict[str, tuple[BM25Okapi, list[dict], int]] = {}

    def build_index(self, project_id: UUID) -> None:
        """(Re)build the BM25 index for a project.

        Args:
            project_id: Project UUID whose chunks to index.
        """
        conn = self._db.get_connection()
        rows = conn.execute(
            """SELECT c.chroma_id, c.content, c.page_number, c.section_heading,
                      c.document_id, d.filename, d.source_tier
               FROM chunks c
               JOIN documents d ON c.document_id = d.id
               WHERE d.project_id = ?
               ORDER BY c.chunk_index""",
            (str(project_id),),
        ).fetchall()

        corpus_tokens: list[list[str]] = []
        chunk_data: list[dict] = []

        for row in rows:
            tokens = _tokenize(row["content"])
            corpus_tokens.append(tokens)
            chunk_data.append({
                "chunk_id": row["chroma_id"],
                "content": row["content"],
                "document_id": row["document_id"],
                "filename": row["filename"] or "",
                "page_number": row["page_number"],
                "section_heading": row["section_heading"] or "",
                "source_tier": row["source_tier"] or "",
            })

        if corpus_tokens:
            bm25 = BM25Okapi(corpus_tokens)
        else:
            bm25 = None  # type: ignore[assignment]

        self._cache[str(project_id)] = (bm25, chunk_data, len(rows))  # type: ignore[arg-type]
        log.info("bm25_index_built", project_id=str(project_id), chunks=len(rows))

    def search(
        self, query: str, project_id: UUID, top_k: int = 20
    ) -> list[SearchResult]:
        """Search for chunks matching the query by keyword relevance.

        Args:
            query: Natural-language query.
            project_id: Project UUID.
            top_k: Maximum results to return.

        Returns:
            Ranked list of SearchResult with normalised BM25 scores in [0, 1].
        """
        pid = str(project_id)

        # Rebuild index if not cached or if document count changed
        current_count = self._get_chunk_count(project_id)
        cached = self._cache.get(pid)
        if cached is None or cached[2] != current_count:
            self.build_index(project_id)
            cached = self._cache.get(pid)

        if cached is None or cached[0] is None:
            return []

        bm25, chunk_data, _ = cached
        query_tokens = _tokenize(query)
        scores = bm25.get_scores(query_tokens)

        # Pair scores with data, sort descending
        scored = sorted(
            zip(scores, chunk_data),
            key=lambda x: x[0],
            reverse=True,
        )

        # Normalise scores to 0-1
        max_score = scored[0][0] if scored and scored[0][0] > 0 else 1.0

        results: list[SearchResult] = []
        for raw_score, data in scored[:top_k]:
            if raw_score <= 0:
                break
            results.append(SearchResult(
                chunk_id=data["chunk_id"],
                content=data["content"],
                score=raw_score / max_score,
                metadata={
                    "document_id": data["document_id"],
                    "filename": data["filename"],
                    "page_number": data["page_number"],
                    "section_heading": data["section_heading"],
                    "source_tier": data["source_tier"],
                },
            ))

        log.info("bm25_search_complete", project_id=pid, results=len(results))
        return results

    def _get_chunk_count(self, project_id: UUID) -> int:
        """Get current chunk count for a project to detect stale cache."""
        conn = self._db.get_connection()
        row = conn.execute(
            """SELECT COUNT(*) FROM chunks c
               JOIN documents d ON c.document_id = d.id
               WHERE d.project_id = ?""",
            (str(project_id),),
        ).fetchone()
        return row[0] if row else 0
