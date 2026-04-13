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
from core.validation.confidence import ConfidenceScorer
from core.validation.cross_reference import CrossReferencer
from core.validation.hallucination import HallucinationDetector
from core.validation.pipeline import ValidationPipeline

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
        validation_pipeline: ValidationPipeline | None = None,
    ) -> None:
        self._vector = vector_searcher
        self._keyword = keyword_searcher
        self._reranker = reranker
        self._context = context_builder
        self._llm = ollama_client
        self._parser = response_parser
        self._top_k_retrieval = top_k_retrieval
        self._top_k_final = top_k_final
        self._validation = validation_pipeline or self._build_default_validation()

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

        # 3.5. Off-topic detection — if no results are sufficiently relevant,
        # return early without calling the LLM to prevent fabricated answers.
        # Use original vector search scores (0-1 similarity) not RRF scores (much smaller).
        max_relevance = max(
            (r.score for r in vector_results), default=0.0
        ) if vector_results else 0.0
        if max_relevance < 0.25 or not reranked:
            log.info("query_off_topic", question=request.question[:80], max_relevance=max_relevance)
            return QueryResponse(
                answer="This question does not appear to relate to the documents in your "
                       "current project. Try importing relevant documents into the Library first, "
                       "or rephrase your question to match topics covered in your sources.",
                citations=[],
                confidence=ConfidenceResult(
                    score=0.0,
                    explanation="No relevant sources found for this question.",
                    flagged_claims=[],
                    alternative_interpretations=[],
                ),
                sources_used=0,
                retrieval_scores={
                    "vector_results": len(vector_results),
                    "keyword_results": len(keyword_results),
                    "fused_results": len(fused),
                    "reranked_results": len(reranked),
                    "max_relevance": max_relevance,
                },
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

        # 7. Validate — every response passes through the validation pipeline
        validated = self._validation.validate_response(
            parsed.answer_text, reranked, parsed.claims,
        )

        return QueryResponse(
            answer=validated.validated_answer,
            citations=parsed.citations,
            confidence=validated.confidence,
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

        # Parse and validate the complete response
        parsed = self._parser.parse_response(full_response, reranked)
        validated = self._validation.validate_response(
            parsed.answer_text, reranked, parsed.claims,
        )

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
                "confidence": validated.confidence.model_dump(mode="json"),
                "flagged_claims": [
                    item.model_dump(mode="json")
                    for item in validated.hallucination_report.flagged_items
                ],
            },
        }

        # Send validation report as separate event
        yield {
            "type": "validation",
            "data": {
                "confidence": validated.confidence.model_dump(mode="json"),
                "hallucination_report": validated.hallucination_report.model_dump(mode="json"),
                "cross_reference_report": validated.cross_reference_report.model_dump(mode="json"),
            },
        }

    def _build_default_validation(self) -> ValidationPipeline:
        """Build a default validation pipeline."""
        from core.validation.source_tier import SourceTierClassifier
        return ValidationPipeline(
            confidence_scorer=ConfidenceScorer(SourceTierClassifier()),
            hallucination_detector=HallucinationDetector(),
            cross_referencer=CrossReferencer(),
        )

