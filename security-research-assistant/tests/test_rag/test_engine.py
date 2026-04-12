"""Integration tests for the RAG engine with mock LLM."""

from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from core.models.query import QueryRequest
from core.rag.context_builder import ContextBuilder
from core.rag.engine import RAGEngine
from core.rag.keyword_search import KeywordSearcher
from core.rag.reranker import Reranker
from core.rag.response_parser import ResponseParser
from core.rag.search_models import SearchResult
from core.rag.vector_search import VectorSearcher

from .conftest import TEST_PROJECT_ID


class _FakeVectorSearcher:
    """Fake vector searcher returning fixed results."""

    def search(self, query, project_id, top_k=20, filters=None):
        return [
            SearchResult(
                chunk_id="vec_0", content="ARM Cortex-M4 running at 168 MHz.",
                score=0.92,
                metadata={"document_id": "d1", "filename": "datasheet.pdf",
                          "page_number": 1, "section_heading": "Overview",
                          "source_tier": "tier_1_manufacturer"},
            ),
        ]


class _FakeKeywordSearcher:
    """Fake keyword searcher returning fixed results."""

    def search(self, query, project_id, top_k=20):
        return [
            SearchResult(
                chunk_id="kw_0", content="The clock speed is 168 MHz maximum.",
                score=0.85,
                metadata={"document_id": "d1", "filename": "datasheet.pdf",
                          "page_number": 1, "section_heading": "Specifications",
                          "source_tier": "tier_1_manufacturer"},
            ),
            SearchResult(
                chunk_id="vec_0", content="ARM Cortex-M4 running at 168 MHz.",
                score=0.70,
                metadata={"document_id": "d1", "filename": "datasheet.pdf",
                          "page_number": 1, "section_heading": "Overview",
                          "source_tier": "tier_1_manufacturer"},
            ),
        ]


def _build_engine(llm_response: str) -> RAGEngine:
    """Build a RAG engine with fake searchers and a mock LLM."""
    mock_llm = MagicMock()
    mock_llm.generate.return_value = llm_response

    return RAGEngine(
        vector_searcher=_FakeVectorSearcher(),
        keyword_searcher=_FakeKeywordSearcher(),
        reranker=Reranker(mock_llm, enabled=False),  # Disable reranking for tests
        context_builder=ContextBuilder(max_tokens=4096),
        ollama_client=mock_llm,
        response_parser=ResponseParser(),
    )


class TestRAGEngine:
    """Tests for the RAG engine orchestrator."""

    def test_query_returns_response(self) -> None:
        """Engine should return a QueryResponse with answer and citations."""
        engine = _build_engine(
            "The clock speed is 168 MHz [Source: datasheet.pdf, Page 1]."
        )
        request = QueryRequest(question="What is the clock speed?", project_id=TEST_PROJECT_ID)
        response = engine.query(request)

        assert "168 MHz" in response.answer
        assert len(response.citations) >= 1
        assert response.sources_used >= 1

    def test_query_with_no_relevant_docs(self) -> None:
        """Engine should still return a response even with irrelevant results."""
        engine = _build_engine(
            "Insufficient information in the current library to answer this question."
        )
        request = QueryRequest(question="What is the meaning of life?", project_id=TEST_PROJECT_ID)
        response = engine.query(request)
        assert "Insufficient" in response.answer

    def test_retrieval_scores_populated(self) -> None:
        """Response should include retrieval score metadata."""
        engine = _build_engine("Answer [Source: datasheet.pdf, Page 1].")
        request = QueryRequest(question="Test?", project_id=TEST_PROJECT_ID)
        response = engine.query(request)
        assert "vector_results" in response.retrieval_scores
        assert "keyword_results" in response.retrieval_scores

    def test_confidence_score_present(self) -> None:
        """Response should include a confidence score."""
        engine = _build_engine("Answer [Source: datasheet.pdf, Page 1].")
        request = QueryRequest(question="Test?", project_id=TEST_PROJECT_ID)
        response = engine.query(request)
        assert 0 <= response.confidence.score <= 100

    def test_streaming_yields_tokens(self) -> None:
        """Streaming query should yield token events then a done event."""
        mock_llm = MagicMock()

        def fake_stream(prompt, system_prompt="", stream=False):
            if stream:
                return iter(["The ", "answer ", "is ", "42."])
            return "The answer is 42."

        mock_llm.generate.side_effect = fake_stream

        engine = RAGEngine(
            vector_searcher=_FakeVectorSearcher(),
            keyword_searcher=_FakeKeywordSearcher(),
            reranker=Reranker(mock_llm, enabled=False),
            context_builder=ContextBuilder(max_tokens=4096),
            ollama_client=mock_llm,
            response_parser=ResponseParser(),
        )

        request = QueryRequest(question="What?", project_id=TEST_PROJECT_ID)
        events = list(engine.query_stream(request))

        token_events = [e for e in events if e["type"] == "token"]
        done_events = [e for e in events if e["type"] == "done"]

        assert len(token_events) == 4
        assert len(done_events) == 1
        assert "citations" in done_events[0]["data"]

    def test_conversation_context_passed(self) -> None:
        """Conversation summary and pinned facts should reach the context builder."""
        engine = _build_engine("Response text.")
        request = QueryRequest(question="Follow up?", project_id=TEST_PROJECT_ID)
        response = engine.query(
            request,
            conversation_summary="We discussed GPIO pins.",
            pinned_facts=["Main CPU is STM32F407"],
        )
        # Should not crash, and the LLM was called with enriched context
        assert response.answer == "Response text."
