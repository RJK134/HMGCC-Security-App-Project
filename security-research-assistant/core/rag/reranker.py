"""LLM-based re-ranking of search results for improved relevance."""

import json
import re

from core.logging import get_logger
from core.rag.llm_client import OllamaClient
from core.rag.search_models import SearchResult

log = get_logger(__name__)

_RERANK_PROMPT = """Rate the relevance of each passage to the question on a scale of 1-10.
Only return a JSON object mapping passage number to score. No explanation needed.

Question: {query}

{passages}

Respond ONLY with JSON like: {{"1": 8, "2": 3, "3": 9}}"""


class Reranker:
    """Re-rank search results using the local LLM for relevance scoring.

    Args:
        ollama_client: Ollama client for LLM calls.
        enabled: Whether re-ranking is active (can be disabled for speed).
    """

    def __init__(self, ollama_client: OllamaClient, enabled: bool = True) -> None:
        self._client = ollama_client
        self._enabled = enabled

    def rerank(
        self, query: str, results: list[SearchResult], top_k: int = 5
    ) -> list[SearchResult]:
        """Re-rank results by LLM-assessed relevance to the query.

        Falls back to original order if LLM call or parsing fails.

        Args:
            query: User's question.
            results: Pre-ranked search results (from RRF).
            top_k: Number of results to return after re-ranking.

        Returns:
            Re-ranked list of the top_k most relevant results.
        """
        if not self._enabled or not results:
            return results[:top_k]

        # Only re-rank the top candidates (max 10)
        candidates = results[:10]

        passages = "\n".join(
            f"Passage {i+1}: {r.content[:200]}"
            for i, r in enumerate(candidates)
        )
        prompt = _RERANK_PROMPT.format(query=query, passages=passages)

        try:
            response = self._client.generate(prompt, system_prompt="")
            if not isinstance(response, str):
                response = "".join(response)  # Exhaust generator if streaming

            scores = self._parse_scores(response, len(candidates))

            # Apply scores
            scored = []
            for i, result in enumerate(candidates):
                llm_score = scores.get(i + 1, 5)  # Default to mid-score
                scored.append((llm_score, result))

            scored.sort(key=lambda x: x[0], reverse=True)
            reranked = [r for _, r in scored[:top_k]]

            log.info("rerank_complete", candidates=len(candidates), returned=len(reranked))
            return reranked

        except Exception as e:
            log.warning("rerank_failed_fallback", error=str(e))
            return candidates[:top_k]

    def _parse_scores(self, response: str, count: int) -> dict[int, float]:
        """Extract passage scores from LLM JSON response."""
        # Try to find JSON in the response
        json_match = re.search(r"\{[^{}]+\}", response)
        if json_match:
            try:
                raw = json.loads(json_match.group())
                return {int(k): float(v) for k, v in raw.items()}
            except (json.JSONDecodeError, ValueError):
                pass

        # Fallback: look for "N: score" patterns
        scores: dict[int, float] = {}
        for match in re.finditer(r'"?(\d+)"?\s*:\s*(\d+(?:\.\d+)?)', response):
            scores[int(match.group(1))] = float(match.group(2))

        return scores
