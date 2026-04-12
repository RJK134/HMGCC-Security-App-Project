"""Query API endpoints with SSE streaming support."""

import json

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from backend.config import Settings
from backend.dependencies import get_app_settings, get_db, get_ollama_client, get_vector_store
from core.database.connection import DatabaseManager
from core.ingest.embedder import Embedder
from core.logging import get_logger
from core.models.query import QueryRequest, QueryResponse
from core.rag.context_builder import ContextBuilder
from core.rag.engine import RAGEngine
from core.rag.keyword_search import KeywordSearcher
from core.rag.llm_client import OllamaClient
from core.rag.reranker import Reranker
from core.rag.response_parser import ResponseParser
from core.rag.vector_search import VectorSearcher
from core.vector_store.chroma_client import ChromaVectorStore

log = get_logger(__name__)
router = APIRouter(tags=["query"])


def _build_engine(
    db: DatabaseManager,
    vector_store: ChromaVectorStore,
    ollama: OllamaClient,
    settings: Settings,
) -> RAGEngine:
    """Assemble the RAG engine from its components."""
    embedder = Embedder(ollama)
    return RAGEngine(
        vector_searcher=VectorSearcher(vector_store, embedder),
        keyword_searcher=KeywordSearcher(db),
        reranker=Reranker(ollama),
        context_builder=ContextBuilder(max_tokens=settings.max_context_tokens),
        ollama_client=ollama,
        response_parser=ResponseParser(),
        top_k_retrieval=settings.top_k * 2,
        top_k_final=settings.top_k,
    )


@router.post("/query")
def query_endpoint(
    request: QueryRequest,
    stream: bool = Query(default=True),
    db: DatabaseManager = Depends(get_db),
    vector_store: ChromaVectorStore = Depends(get_vector_store),
    ollama: OllamaClient = Depends(get_ollama_client),
    settings: Settings = Depends(get_app_settings),
):
    """Submit a question and get a streamed or complete response.

    When stream=true (default), returns SSE events:
      event: token  data: {"token": "..."}
      event: done   data: {"citations": [...], ...}

    When stream=false, returns the complete QueryResponse as JSON.
    """
    engine = _build_engine(db, vector_store, ollama, settings)

    # TODO Sprint 2.2: load conversation context
    conversation_summary = None
    pinned_facts = None

    if not stream:
        response = engine.query(request, conversation_summary, pinned_facts)
        return response.model_dump(mode="json")

    # SSE streaming
    def event_stream():
        try:
            for event in engine.query_stream(request, conversation_summary, pinned_facts):
                if event["type"] == "token":
                    yield f"event: token\ndata: {json.dumps({'token': event['data']})}\n\n"
                elif event["type"] == "done":
                    yield f"event: done\ndata: {json.dumps(event['data'])}\n\n"
                elif event["type"] == "error":
                    yield f"event: error\ndata: {json.dumps({'error': event['data']})}\n\n"
        except Exception as e:
            log.error("stream_error", error=str(e))
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/query/simple")
def query_simple(
    request: QueryRequest,
    db: DatabaseManager = Depends(get_db),
    vector_store: ChromaVectorStore = Depends(get_vector_store),
    ollama: OllamaClient = Depends(get_ollama_client),
    settings: Settings = Depends(get_app_settings),
) -> dict:
    """Non-streaming convenience endpoint returning the full response as JSON."""
    engine = _build_engine(db, vector_store, ollama, settings)
    response = engine.query(request)
    return response.model_dump(mode="json")
