"""Conversation management API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from backend.config import Settings
from backend.dependencies import get_app_settings, get_db, get_ollama_client
from core.conversation.manager import ConversationManager
from core.conversation.memory import MemoryManager
from core.conversation.summariser import ConversationSummariser
from core.database.connection import DatabaseManager
from core.logging import get_logger
from core.models.conversation import Citation
from core.rag.llm_client import OllamaClient

log = get_logger(__name__)
router = APIRouter(prefix="/conversations", tags=["conversations"])


# --- Request schemas ---

class CreateConversationRequest(BaseModel):
    project_id: UUID
    title: str


class PinFactRequest(BaseModel):
    content: str
    source_refs: list[Citation] = Field(default_factory=list)


# --- Helpers ---

def _get_manager(db: DatabaseManager, ollama: OllamaClient) -> ConversationManager:
    summariser = ConversationSummariser(ollama)
    return ConversationManager(db, summariser)


def _get_memory(db: DatabaseManager) -> MemoryManager:
    return MemoryManager(db)


# --- Endpoints ---

@router.post("")
def create_conversation(
    request: CreateConversationRequest,
    db: DatabaseManager = Depends(get_db),
    ollama: OllamaClient = Depends(get_ollama_client),
) -> dict:
    """Create a new conversation for a project."""
    manager = _get_manager(db, ollama)
    conv = manager.create_conversation(request.project_id, request.title)
    return {"conversation": conv.model_dump(mode="json")}


@router.get("")
def list_conversations(
    project_id: UUID,
    db: DatabaseManager = Depends(get_db),
    ollama: OllamaClient = Depends(get_ollama_client),
) -> dict:
    """List all conversations for a project."""
    manager = _get_manager(db, ollama)
    conversations = manager.list_conversations(project_id)
    return {"conversations": conversations}


@router.get("/{conversation_id}")
def get_conversation(
    conversation_id: UUID,
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: DatabaseManager = Depends(get_db),
    ollama: OllamaClient = Depends(get_ollama_client),
) -> dict:
    """Get a conversation with messages (paginated) and pinned facts."""
    manager = _get_manager(db, ollama)
    conv = manager.get_conversation(conversation_id)

    # Paginate messages
    all_messages = conv.messages
    paginated = all_messages[offset : offset + limit]

    return {
        "conversation": {
            "id": str(conv.id),
            "project_id": str(conv.project_id),
            "title": conv.title,
            "summary": conv.summary,
            "created_at": conv.created_at.isoformat(),
            "updated_at": conv.updated_at.isoformat(),
            "message_count": len(all_messages),
        },
        "messages": [m.model_dump(mode="json") for m in paginated],
        "pinned_facts": [f.model_dump(mode="json") for f in conv.pinned_facts],
        "pagination": {"total": len(all_messages), "limit": limit, "offset": offset},
    }


@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: UUID,
    db: DatabaseManager = Depends(get_db),
    ollama: OllamaClient = Depends(get_ollama_client),
) -> dict:
    """Delete a conversation and all its data."""
    manager = _get_manager(db, ollama)
    manager.delete_conversation(conversation_id)
    return {"status": "ok", "conversation_id": str(conversation_id)}


@router.post("/{conversation_id}/pin")
def pin_fact(
    conversation_id: UUID,
    request: PinFactRequest,
    db: DatabaseManager = Depends(get_db),
) -> dict:
    """Pin a key finding to a conversation."""
    memory = _get_memory(db)
    fact = memory.pin_fact(conversation_id, request.content, request.source_refs)
    return {"pinned_fact": fact.model_dump(mode="json")}


@router.get("/{conversation_id}/pins")
def get_pinned_facts(
    conversation_id: UUID,
    db: DatabaseManager = Depends(get_db),
) -> dict:
    """Get all pinned facts for a conversation."""
    memory = _get_memory(db)
    facts = memory.get_pinned_facts(conversation_id)
    return {"pinned_facts": [f.model_dump(mode="json") for f in facts]}


@router.delete("/{conversation_id}/pins/{fact_id}")
def unpin_fact(
    conversation_id: UUID,
    fact_id: UUID,
    db: DatabaseManager = Depends(get_db),
) -> dict:
    """Remove a pinned fact."""
    memory = _get_memory(db)
    memory.unpin_fact(fact_id)
    return {"status": "ok", "fact_id": str(fact_id)}


@router.post("/{conversation_id}/suggest-pins")
def suggest_pins(
    conversation_id: UUID,
    db: DatabaseManager = Depends(get_db),
    ollama: OllamaClient = Depends(get_ollama_client),
) -> dict:
    """Suggest facts to pin based on recent messages."""
    manager = _get_manager(db, ollama)
    memory = _get_memory(db)
    summariser = ConversationSummariser(ollama)

    conv = manager.get_conversation(conversation_id)
    recent = conv.messages[-6:] if conv.messages else []
    suggestions = memory.suggest_facts_to_pin(conversation_id, recent, summariser)
    return {"suggestions": suggestions}


@router.post("/{conversation_id}/summarise")
def force_summarise(
    conversation_id: UUID,
    db: DatabaseManager = Depends(get_db),
    ollama: OllamaClient = Depends(get_ollama_client),
) -> dict:
    """Force a summary regeneration for a conversation."""
    manager = _get_manager(db, ollama)
    summary = manager.update_summary(conversation_id)
    return {"summary": summary}
