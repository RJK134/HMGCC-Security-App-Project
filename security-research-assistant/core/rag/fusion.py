"""Reciprocal Rank Fusion to merge vector and keyword search results."""

from core.logging import get_logger
from core.rag.search_models import SearchResult

log = get_logger(__name__)


def fuse_results(
    vector_results: list[SearchResult],
    keyword_results: list[SearchResult],
    k: int = 60,
    top_k: int = 10,
) -> list[SearchResult]:
    """Merge results from vector and keyword search using Reciprocal Rank Fusion.

    RRF score for document d = sum(1 / (k + rank_i(d))) across all result lists
    where rank_i is the 1-based rank in list i.

    Args:
        vector_results: Ranked results from vector similarity search.
        keyword_results: Ranked results from BM25 keyword search.
        k: RRF constant (default 60, standard in literature).
        top_k: Number of fused results to return.

    Returns:
        Top-k results sorted by fused RRF score descending.
    """
    rrf_scores: dict[str, float] = {}
    chunk_map: dict[str, SearchResult] = {}

    # Score from vector results
    for rank, result in enumerate(vector_results, start=1):
        rrf_scores[result.chunk_id] = rrf_scores.get(result.chunk_id, 0.0) + 1.0 / (k + rank)
        if result.chunk_id not in chunk_map:
            chunk_map[result.chunk_id] = result

    # Score from keyword results
    for rank, result in enumerate(keyword_results, start=1):
        rrf_scores[result.chunk_id] = rrf_scores.get(result.chunk_id, 0.0) + 1.0 / (k + rank)
        if result.chunk_id not in chunk_map:
            chunk_map[result.chunk_id] = result

    # Apply source tier boost — manufacturer docs rank higher than unverified
    _TIER_BOOST: dict[str, float] = {
        "tier_1_manufacturer": 1.0,
        "tier_2_academic": 0.9,
        "tier_3_trusted_forum": 0.75,
        "tier_4_unverified": 0.65,
    }
    for chunk_id in rrf_scores:
        tier = chunk_map[chunk_id].metadata.get("source_tier", "tier_4_unverified")
        boost = _TIER_BOOST.get(tier, 0.65)
        rrf_scores[chunk_id] *= (0.5 + 0.5 * boost)  # Compressed range: 0.825-1.0

    # Sort by boosted fused score
    ranked = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

    results: list[SearchResult] = []
    for chunk_id, fused_score in ranked[:top_k]:
        original = chunk_map[chunk_id]
        results.append(SearchResult(
            chunk_id=chunk_id,
            content=original.content,
            score=fused_score,
            metadata=original.metadata,
        ))

    log.info(
        "rrf_fusion_complete",
        vector_count=len(vector_results),
        keyword_count=len(keyword_results),
        fused_count=len(results),
    )
    return results
