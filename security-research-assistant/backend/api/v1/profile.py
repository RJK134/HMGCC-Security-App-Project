"""User profile and notification API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.dependencies import get_db, get_ollama_client, get_vector_store
from core.database.connection import DatabaseManager
from core.logging import get_logger
from core.models.document import SourceTier
from core.profile.proactive import ProactiveEngine
from core.profile.tracker import PreferenceTracker
from core.rag.llm_client import OllamaClient
from core.vector_store.chroma_client import ChromaVectorStore

log = get_logger(__name__)
router = APIRouter(tags=["profile"])


class PreferenceUpdate(BaseModel):
    detail_preference: float | None = None
    format_preference: str | None = None
    custom_preferences: dict | None = None


@router.get("/profile")
def get_profile(db: DatabaseManager = Depends(get_db)) -> dict:
    """Return the current user profile."""
    tracker = PreferenceTracker(db)
    return {"profile": tracker.export_profile()}


@router.put("/profile/preferences")
def update_preferences(
    request: PreferenceUpdate,
    db: DatabaseManager = Depends(get_db),
) -> dict:
    """Manually set or override preferences."""
    tracker = PreferenceTracker(db)
    profile = tracker.get_profile()

    if request.detail_preference is not None:
        profile.detail_preference = max(0.0, min(1.0, request.detail_preference))
    if request.format_preference is not None:
        profile.format_preference = request.format_preference
    if request.custom_preferences is not None:
        profile.custom_preferences.update(request.custom_preferences)

    tracker._save_profile(profile)
    return {"profile": tracker.export_profile()}


@router.delete("/profile")
def reset_profile(db: DatabaseManager = Depends(get_db)) -> dict:
    """Reset profile to defaults."""
    tracker = PreferenceTracker(db)
    tracker.reset_profile()
    return {"status": "ok"}


@router.get("/profile/export")
def export_profile(db: DatabaseManager = Depends(get_db)) -> dict:
    """Export profile as JSON."""
    tracker = PreferenceTracker(db)
    return tracker.export_profile()


@router.post("/profile/import")
def import_profile(
    profile_data: dict,
    db: DatabaseManager = Depends(get_db),
) -> dict:
    """Import a previously exported profile."""
    tracker = PreferenceTracker(db)
    tracker.import_profile(profile_data)
    return {"status": "ok", "profile": tracker.export_profile()}


@router.get("/notifications")
def get_notifications(
    project_id: UUID,
    db: DatabaseManager = Depends(get_db),
    vector_store: ChromaVectorStore = Depends(get_vector_store),
) -> dict:
    """Return proactive notifications for relevant new content."""
    tracker = PreferenceTracker(db)
    profile = tracker.get_profile()
    engine = ProactiveEngine(db, vector_store)
    notifications = engine.check_for_relevant_updates(project_id, profile)
    return {"notifications": [n.model_dump(mode="json") for n in notifications]}
