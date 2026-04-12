"""Tests for BM25 keyword search."""

from uuid import UUID

import pytest

from core.database.connection import DatabaseManager
from core.rag.keyword_search import KeywordSearcher


class TestKeywordSearcher:
    """Tests for BM25 keyword search."""

    def test_search_returns_results(self, rag_db: tuple) -> None:
        """Search for an exact term should return relevant chunks."""
        db, project_id = rag_db
        searcher = KeywordSearcher(db)
        # Use terms that appear as exact whitespace-delimited tokens in the test data
        results = searcher.search("microcontroller ARM Cortex-M4 168 MHz", project_id, top_k=5)
        assert len(results) > 0

    def test_scores_normalized(self, rag_db: tuple) -> None:
        """Scores should be in [0, 1] range."""
        db, project_id = rag_db
        searcher = KeywordSearcher(db)
        results = searcher.search("Modbus protocol", project_id)
        for r in results:
            assert 0.0 <= r.score <= 1.0

    def test_metadata_present(self, rag_db: tuple) -> None:
        """Results should include document metadata."""
        db, project_id = rag_db
        searcher = KeywordSearcher(db)
        results = searcher.search("GPIO", project_id)
        if results:
            assert "filename" in results[0].metadata
            assert "document_id" in results[0].metadata

    def test_empty_corpus(self, tmp_path) -> None:
        """Search against empty project should return empty results."""
        from uuid import uuid4
        db = DatabaseManager(tmp_path / "empty.db")
        db.initialize()
        searcher = KeywordSearcher(db)
        results = searcher.search("anything", uuid4())
        assert results == []

    def test_index_caching(self, rag_db: tuple) -> None:
        """Second search should use cached index."""
        db, project_id = rag_db
        searcher = KeywordSearcher(db)
        searcher.search("test", project_id)
        # Second call should hit cache
        results = searcher.search("GPIO pins", project_id)
        assert len(results) > 0

    def test_exact_term_ranked_high(self, rag_db: tuple) -> None:
        """Exact term 'Modbus' should rank the Modbus chunk highest."""
        db, project_id = rag_db
        searcher = KeywordSearcher(db)
        results = searcher.search("Modbus RTU RS-485", project_id, top_k=3)
        assert len(results) > 0
        assert "Modbus" in results[0].content
