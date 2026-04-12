"""Query API endpoints with SSE streaming and conversation context support."""

import json
from uuid import uuid4

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from backend.config import Settings
from backend.dependencies import get_app_settings, get_db, get_ollama_client, get_vector_store
from core.conversation.manager import ConversationManager
from core.conversation.memory import MemoryManager
from core.conversation.summariser import ConversationSummariser
from core.database.connection import DatabaseManager
from core.ingest.embedder import Embedder
from core.logging import get_logger
from core.models.conversation import MessageRole
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


def _get_conversation_manager(
    db: DatabaseManager, ollama: OllamaClient,
) -> ConversationManager:
    """Build a ConversationManager with summariser."""
    summariser = ConversationSummariser(ollama)
    return ConversationManager(db, summariser)


def _load_conversation_context(
    conv_manager: ConversationManager,
    request: QueryRequest,
) -> tuple[str | None, list[str] | None, "UUID | None"]:
    """Load conversation context or create a new conversation.

    Returns (summary, pinned_fact_strings, conversation_id).
    """
    conversation_id = request.conversation_id

    if conversation_id is None:
        # Auto-create a conversation
        conv = conv_manager.create_conversation(
            request.project_id,
            title=request.question[:60],
        )
        conversation_id = conv.id

    ctx = conv_manager.get_context_for_query(conversation_id)
    pinned_strs = [f.content for f in ctx.pinned_facts] if ctx.pinned_facts else None

    return ctx.summary, pinned_strs, conversation_id


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

    Automatically loads conversation context (summary + pinned facts) if
    conversation_id is provided. If not, creates a new conversation.

    When stream=true (default), returns SSE events.
    When stream=false, returns the complete QueryResponse as JSON.
    """
    engine = _build_engine(db, vector_store, ollama, settings)
    conv_manager = _get_conversation_manager(db, ollama)

    summary, pinned_facts, conversation_id = _load_conversation_context(conv_manager, request)

    # Store user message
    conv_manager.add_message(conversation_id, MessageRole.USER, request.question)

    if not stream:
        response = engine.query(request, summary, pinned_facts)

        # Store assistant response
        conv_manager.add_message(
            conversation_id, MessageRole.ASSISTANT, response.answer,
            citations=response.citations,
            confidence_score=response.confidence.score,
        )

        result = response.model_dump(mode="json")
        result["conversation_id"] = str(conversation_id)
        return result

    # SSE streaming
    def event_stream():
        full_response = ""
        try:
            for event in engine.query_stream(request, summary, pinned_facts):
                if event["type"] == "token":
                    full_response += event["data"]
                    yield f"event: token\ndata: {json.dumps({'token': event['data']})}\n\n"
                elif event["type"] == "done":
                    # Store assistant response
                    try:
                        conv_manager.add_message(
                            conversation_id, MessageRole.ASSISTANT, full_response,
                        )
                    except Exception as store_err:
                        log.warning("message_store_failed", error=str(store_err))

                    event["data"]["conversation_id"] = str(conversation_id)
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
    conv_manager = _get_conversation_manager(db, ollama)

    summary, pinned_facts, conversation_id = _load_conversation_context(conv_manager, request)
    conv_manager.add_message(conversation_id, MessageRole.USER, request.question)

    response = engine.query(request, summary, pinned_facts)

    conv_manager.add_message(
        conversation_id, MessageRole.ASSISTANT, response.answer,
        citations=response.citations,
        confidence_score=response.confidence.score,
    )

    result = response.model_dump(mode="json")
    result["conversation_id"] = str(conversation_id)
    return result
