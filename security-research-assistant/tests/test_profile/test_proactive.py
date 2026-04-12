"""Tests for ProactiveEngine notifications."""

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest

from core.database.connection import DatabaseManager
from core.models.profile import UserProfile
from core.profile.proactive import ProactiveEngine
from core.vector_store.chroma_client import ChromaVectorStore


@pytest.fixture
def proactive_env(tmp_path: Path):
    db = DatabaseManager(tmp_path / "proactive.db")
    db.initialize()
    conn = db.get_connection()

    project_id = uuid4()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO projects (id, name, created_at, updated_at) VALUES (?, ?, ?, ?)",
        (str(project_id), "Proactive Test", now, now),
    )
    doc_id = uuid4()
    conn.execute(
        "INSERT INTO documents (id, project_id, filename, filepath, filetype, "
        "size_bytes, status, source_tier, import_timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (str(doc_id), str(project_id), "spi_datasheet.pdf", "/spi.pdf", "pdf",
         1000, "indexed", "tier_1_manufacturer", now),
    )
    conn.execute(
        "INSERT INTO chunks (id, document_id, content, chunk_index, page_number, "
        "section_heading, token_count, chroma_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (str(uuid4()), str(doc_id),
         "The SPI bus operates at 42 MHz with full-duplex communication.",
         0, 1, "SPI Interface", 15, f"{doc_id}_0"),
    )
    conn.commit()

    vs = ChromaVectorStore(tmp_path / "chroma")
    return db, vs, project_id


class TestProactiveEngine:
    def test_detects_relevant_update(self, proactive_env) -> None:
        db, vs, project_id = proactive_env
        profile = UserProfile(frequent_topics=["spi", "bus"])
        engine = ProactiveEngine(db, vs)
        notifications = engine.check_for_relevant_updates(project_id, profile)
        assert len(notifications) >= 1
        assert "spi" in notifications[0].topic.lower()

    def test_no_notifications_for_unrelated(self, proactive_env) -> None:
        db, vs, project_id = proactive_env
        profile = UserProfile(frequent_topics=["bluetooth", "wifi"])
        engine = ProactiveEngine(db, vs)
        notifications = engine.check_for_relevant_updates(project_id, profile)
        assert len(notifications) == 0

    def test_no_topics_no_notifications(self, proactive_env) -> None:
        db, vs, project_id = proactive_env
        profile = UserProfile()  # No topics
        engine = ProactiveEngine(db, vs)
        notifications = engine.check_for_relevant_updates(project_id, profile)
        assert len(notifications) == 0

    def test_notification_format(self, proactive_env) -> None:
        db, vs, project_id = proactive_env
        profile = UserProfile(frequent_topics=["spi"])
        engine = ProactiveEngine(db, vs)
        notifications = engine.check_for_relevant_updates(project_id, profile)
        if notifications:
            n = notifications[0]
            assert n.message
            assert n.document_name
            assert n.relevance_score > 0
