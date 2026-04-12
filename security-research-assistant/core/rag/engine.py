"""RAG engine orchestrator — coordinates search, context assembly, and generation."""

from collections.abc import Generator
from uuid import UUID

from core.logging import get_logger
from core.models.conversation import Citation
from core.models.query import ConfidenceResult, QueryRequest, QueryResponse
from core.rag.context_builder import ContextBuilder
from core.rag.fusion import fuse_results
from core.rag.keyword_search import KeywordSearcher
from core.rag.llm_client import OllamaClient
from core.rag.reranker import Reranker
from core.rag.response_parser import ResponseParser
from core.rag.search_models import SearchResult
from core.rag.vector_search import VectorSearcher

log = get_logger(__name__)


class RAGEngine:
    """Orchestrate the full RAG pipeline: search → fuse → rerank → generate → parse.

    Args:
        vector_searcher: Semantic vector search.
        keyword_searcher: BM25 keyword search.
        reranker: LLM-based re-ranker (optional, can be disabled).
        context_builder: Prompt assembler with token budget.
        ollama_client: Local LLM client.
        response_parser: Citation and claim extractor.
        top_k_retrieval: How many chunks to retrieve from each search.
        top_k_final: How many chunks to include in context after reranking.
    """

    def __init__(
        self,
        vector_searcher: VectorSearcher,
        keyword_searcher: KeywordSearcher,
        reranker: Reranker,
        context_builder: ContextBuilder,
        ollama_client: OllamaClient,
        response_parser: ResponseParser,
        top_k_retrieval: int = 20,
        top_k_final: int = 5,
    ) -> None:
        self._vector = vector_searcher
        self._keyword = keyword_searcher
        self._reranker = reranker
        self._context = context_builder
        self._llm = ollama_client
        self._parser = response_parser
        self._top_k_retrieval = top_k_retrieval
        self._top_k_final = top_k_final

    def query(
        self,
        request: QueryRequest,
        conversation_summary: str | None = None,
        pinned_facts: list[str] | None = None,
    ) -> QueryResponse:
        """Execute the full RAG pipeline and return a complete response.

        Args:
            request: Query with question and project_id.
            conversation_summary: Summary of prior conversation for context.
            pinned_facts: Key facts to include in prompt context.

        Returns:
            QueryResponse with answer, citations, and confidence placeholder.
        """
        # 1. Dual search
        vector_results = self._vector.search(
            request.question, request.project_id, top_k=self._top_k_retrieval,
        )
        keyword_results = self._keyword.search(
            request.question, request.project_id, top_k=self._top_k_retrieval,
        )

        log.info(
            "search_complete",
            vector_hits=len(vector_results),
            keyword_hits=len(keyword_results),
        )

        # 2. Fuse
        fused = fuse_results(
            vector_results, keyword_results, top_k=self._top_k_final * 2,
        )

        # 3. Rerank
        reranked = self._reranker.rerank(
            request.question, fused, top_k=self._top_k_final,
        )

        # 4. Build context
        system_prompt, user_prompt = self._context.build_context(
            request.question, reranked, conversation_summary, pinned_facts,
        )

        # 5. Generate
        log.info("llm_generating", question=request.question[:80])
        response_text = self._llm.generate(user_prompt, system_prompt=system_prompt)
        if not isinstance(response_text, str):
            response_text = "".join(response_text)

        # 6. Parse
        parsed = self._parser.parse_response(response_text, reranked)

        # 7. Build response (confidence scoring deferred to Sprint 2.3)
        confidence = ConfidenceResult(
            score=self._estimate_confidence(parsed.citations, reranked),
            explanation=self._confidence_explanation(parsed.citations, reranked),
        )

        return QueryResponse(
            answer=parsed.answer_text,
            citations=parsed.citations,
            confidence=confidence,
            sources_used=len(parsed.citations),
            retrieval_scores={
                "vector_results": len(vector_results),
                "keyword_results": len(keyword_results),
                "fused_results": len(fused),
                "reranked_results": len(reranked),
            },
        )

    def query_stream(
        self,
        request: QueryRequest,
        conversation_summary: str | None = None,
        pinned_facts: list[str] | None = None,
    ) -> Generator[dict, None, None]:
        """Execute the RAG pipeline with streaming LLM output.

        Yields dicts: {"type": "token", "data": "..."} for each token,
        then a final {"type": "done", "data": {...}} with metadata.

        Args:
            request: Query with question and project_id.
            conversation_summary: Summary of prior conversation.
            pinned_facts: Key facts to include.

        Yields:
            Stream event dicts.
        """
        # Search + fuse + rerank (same as non-streaming)
        vector_results = self._vector.search(
            request.question, request.project_id, top_k=self._top_k_retrieval,
        )
        keyword_results = self._keyword.search(
            request.question, request.project_id, top_k=self._top_k_retrieval,
        )
        fused = fuse_results(
            vector_results, keyword_results, top_k=self._top_k_final * 2,
        )
        reranked = self._reranker.rerank(
            request.question, fused, top_k=self._top_k_final,
        )
        system_prompt, user_prompt = self._context.build_context(
            request.question, reranked, conversation_summary, pinned_facts,
        )

        # Stream from LLM
        full_response = ""
        try:
            stream = self._llm.generate(user_prompt, system_prompt=system_prompt, stream=True)
            if isinstance(stream, str):
                full_response = stream
                yield {"type": "token", "data": stream}
            else:
                for token in stream:
                    full_response += token
                    yield {"type": "token", "data": token}
        except Exception as e:
            yield {"type": "error", "data": str(e)}
            return

        # Parse the complete response
        parsed = self._parser.parse_response(full_response, reranked)

        yield {
            "type": "done",
            "data": {
                "citations": [c.model_dump(mode="json") for c in parsed.citations],
                "sources_used": len(parsed.citations),
                "retrieval_scores": {
                    "vector_results": len(vector_results),
                    "keyword_results": len(keyword_results),
                    "fused_results": len(fused),
                    "reranked_results": len(reranked),
                },
                "confidence": self._estimate_confidence(parsed.citations, reranked),
            },
        }

    def _estimate_confidence(
        self, citations: list[Citation], results: list[SearchResult]
    ) -> float:
        """Basic confidence estimate based on source count and quality.

        Full confidence scoring is built in Sprint 2.3.
        """
        if not citations and not results:
            return 0.0
        if not results:
            return 10.0

        score = min(len(citations) * 15, 50)  # Up to 50 from citation count

        # Boost for high-tier sources
        for r in results:
            tier = r.metadata.get("source_tier", "")
            if "tier_1" in tier:
                score += 10
            elif "tier_2" in tier:
                score += 5

        return min(score, 100.0)

    def _confidence_explanation(
        self, citations: list[Citation], results: list[SearchResult]
    ) -> str:
        """Generate a human-readable confidence explanation."""
        if not citations:
            return "No sources cited in response."
        parts = [f"Based on {len(citations)} cited source(s)."]
        tier_counts: dict[str, int] = {}
        for r in results:
            tier = r.metadata.get("source_tier", "unknown")
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        if tier_counts:
            parts.append("Source tiers: " + ", ".join(f"{k}: {v}" for k, v in tier_counts.items()))
        return " ".join(parts)
