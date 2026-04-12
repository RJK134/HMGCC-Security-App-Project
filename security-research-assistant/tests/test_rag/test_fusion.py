"""Tests for Reciprocal Rank Fusion."""

from core.rag.fusion import fuse_results
from core.rag.search_models import SearchResult


def _make(chunk_id: str, score: float) -> SearchResult:
    return SearchResult(chunk_id=chunk_id, content=f"content {chunk_id}", score=score, metadata={})


class TestFuseResults:
    """Tests for RRF fusion."""

    def test_overlapping_results(self) -> None:
        """Chunks appearing in both lists should score higher."""
        vec = [_make("A", 0.9), _make("B", 0.8), _make("C", 0.7)]
        kw = [_make("B", 0.95), _make("A", 0.6), _make("D", 0.5)]
        fused = fuse_results(vec, kw, top_k=4)

        # A and B appear in both → highest scores
        ids = [r.chunk_id for r in fused]
        assert ids[0] in ("A", "B")
        assert ids[1] in ("A", "B")

    def test_single_list_only(self) -> None:
        """Chunks in only one list still get a score."""
        vec = [_make("X", 0.9)]
        kw = [_make("Y", 0.8)]
        fused = fuse_results(vec, kw, top_k=5)
        ids = {r.chunk_id for r in fused}
        assert "X" in ids
        assert "Y" in ids

    def test_top_k_limiting(self) -> None:
        """Should return at most top_k results."""
        vec = [_make(f"v{i}", 0.9 - i * 0.1) for i in range(10)]
        kw = [_make(f"k{i}", 0.9 - i * 0.1) for i in range(10)]
        fused = fuse_results(vec, kw, top_k=3)
        assert len(fused) == 3

    def test_descending_score_order(self) -> None:
        """Results should be sorted by score descending."""
        vec = [_make("A", 0.5), _make("B", 0.9)]
        kw = [_make("C", 0.7), _make("A", 0.3)]
        fused = fuse_results(vec, kw, top_k=10)
        scores = [r.score for r in fused]
        assert scores == sorted(scores, reverse=True)

    def test_empty_inputs(self) -> None:
        """Empty inputs should return empty results."""
        assert fuse_results([], [], top_k=5) == []

    def test_one_empty_list(self) -> None:
        """One empty list should still return results from the other."""
        vec = [_make("A", 0.9)]
        fused = fuse_results(vec, [], top_k=5)
        assert len(fused) == 1
        assert fused[0].chunk_id == "A"
