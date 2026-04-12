"""Tests for SQLite database layer — connection, schema, and repositories."""

import sqlite3
from pathlib import Path
from uuid import uuid4

import pytest

from core.database.connection import DatabaseManager
from core.database.repositories.conversation_repo import ConversationRepository
from core.database.repositories.document_repo import DocumentRepository
from core.database.repositories.project_repo import ProjectRepository
from core.models.conversation import MessageRole
from core.models.document import DocumentStatus, DocumentType, SourceTier


class TestDatabaseManager:
    """Tests for database initialisation and connection."""

    def test_initialize_creates_tables(self, db_manager: DatabaseManager) -> None:
        """initialize() should create all required tables."""
        conn = db_manager.get_connection()
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        table_names = {row["name"] for row in tables}
        expected = {
            "projects", "documents", "chunks", "conversations",
            "messages", "pinned_facts", "user_profiles", "source_tiers",
            "schema_version",
        }
        assert expected.issubset(table_names)

    def test_schema_version_recorded(self, db_manager: DatabaseManager) -> None:
        """Schema version should be stored after initialization."""
        conn = db_manager.get_connection()
        row = conn.execute("SELECT version FROM schema_version WHERE id = 1").fetchone()
        assert row is not None
        assert row["version"] >= 1

    def test_wal_mode_enabled(self, db_manager: DatabaseManager) -> None:
        """Database should use WAL journal mode."""
        conn = db_manager.get_connection()
        mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        assert mode == "wal"

    def test_close_and_reopen(self, tmp_dir: Path) -> None:
        """Closing and reopening should work without errors."""
        db_path = tmp_dir / "reopen.db"
        manager = DatabaseManager(db_path=db_path)
        manager.initialize()
        manager.close()
        # Reopen
        manager2 = DatabaseManager(db_path=db_path)
        conn = manager2.get_connection()
        conn.execute("SELECT 1")
        manager2.close()


class TestProjectRepository:
    """Tests for project CRUD operations."""

    def test_create_project(self, db_conn, project_repo) -> None:
        """create() should return a Project with generated ID and timestamps."""
        project = project_repo.create(db_conn, name="Test", description="A test project")
        assert project.name == "Test"
        assert project.description == "A test project"
        assert project.id is not None

    def test_get_by_id(self, db_conn, project_repo) -> None:
        """get_by_id() should return the correct project."""
        created = project_repo.create(db_conn, name="Lookup Test")
        found = project_repo.get_by_id(db_conn, created.id)
        assert found is not None
        assert found.name == "Lookup Test"

    def test_get_by_id_not_found(self, db_conn, project_repo) -> None:
        """get_by_id() should return None for non-existent ID."""
        result = project_repo.get_by_id(db_conn, uuid4())
        assert result is None

    def test_list_all(self, db_conn, project_repo) -> None:
        """list_all() should return all projects."""
        project_repo.create(db_conn, name="Project A")
        project_repo.create(db_conn, name="Project B")
        projects = project_repo.list_all(db_conn)
        assert len(projects) >= 2

    def test_update_project(self, db_conn, project_repo) -> None:
        """update() should modify name and description."""
        created = project_repo.create(db_conn, name="Old Name")
        updated = project_repo.update(db_conn, created.id, name="New Name", description="Updated")
        assert updated is not None
        assert updated.name == "New Name"
        assert updated.description == "Updated"

    def test_delete_project(self, db_conn, project_repo) -> None:
        """delete() should remove the project."""
        created = project_repo.create(db_conn, name="To Delete")
        assert project_repo.delete(db_conn, created.id) is True
        assert project_repo.get_by_id(db_conn, created.id) is None

    def test_delete_nonexistent(self, db_conn, project_repo) -> None:
        """delete() should return False for non-existent ID."""
        assert project_repo.delete(db_conn, uuid4()) is False


class TestDocumentRepository:
    """Tests for document CRUD operations."""

    def test_create_document(self, db_conn, document_repo, sample_project_id) -> None:
        """create() should return a DocumentMetadata with correct fields."""
        doc = document_repo.create(
            db_conn,
            project_id=sample_project_id,
            filename="manual.pdf",
            filepath=Path("/data/manual.pdf"),
            filetype=DocumentType.PDF,
            size_bytes=50000,
        )
        assert doc.filename == "manual.pdf"
        assert doc.status == DocumentStatus.PENDING
        assert doc.source_tier == SourceTier.TIER_4_UNVERIFIED

    def test_get_by_id(self, db_conn, document_repo, sample_project_id) -> None:
        """get_by_id() should return the correct document."""
        created = document_repo.create(
            db_conn, project_id=sample_project_id,
            filename="test.pdf", filepath=Path("/test.pdf"),
            filetype=DocumentType.PDF, size_bytes=100,
        )
        found = document_repo.get_by_id(db_conn, created.id)
        assert found is not None
        assert found.filename == "test.pdf"

    def test_list_by_project(self, db_conn, document_repo, sample_project_id) -> None:
        """list_by_project() should return only that project's documents."""
        document_repo.create(
            db_conn, project_id=sample_project_id,
            filename="a.pdf", filepath=Path("/a.pdf"),
            filetype=DocumentType.PDF, size_bytes=100,
        )
        document_repo.create(
            db_conn, project_id=sample_project_id,
            filename="b.png", filepath=Path("/b.png"),
            filetype=DocumentType.IMAGE, size_bytes=200,
        )
        docs = document_repo.list_by_project(db_conn, sample_project_id)
        assert len(docs) == 2

    def test_update_status(self, db_conn, document_repo, sample_project_id) -> None:
        """update_status() should change the document status."""
        doc = document_repo.create(
            db_conn, project_id=sample_project_id,
            filename="s.pdf", filepath=Path("/s.pdf"),
            filetype=DocumentType.PDF, size_bytes=100,
        )
        assert document_repo.update_status(db_conn, doc.id, DocumentStatus.INDEXED)
        updated = document_repo.get_by_id(db_conn, doc.id)
        assert updated is not None
        assert updated.status == DocumentStatus.INDEXED

    def test_update_tier(self, db_conn, document_repo, sample_project_id) -> None:
        """update_tier() should change the source quality tier."""
        doc = document_repo.create(
            db_conn, project_id=sample_project_id,
            filename="ds.pdf", filepath=Path("/ds.pdf"),
            filetype=DocumentType.PDF, size_bytes=100,
        )
        assert document_repo.update_tier(db_conn, doc.id, SourceTier.TIER_1_MANUFACTURER)
        updated = document_repo.get_by_id(db_conn, doc.id)
        assert updated is not None
        assert updated.source_tier == SourceTier.TIER_1_MANUFACTURER

    def test_delete_document(self, db_conn, document_repo, sample_project_id) -> None:
        """delete() should remove the document."""
        doc = document_repo.create(
            db_conn, project_id=sample_project_id,
            filename="del.pdf", filepath=Path("/del.pdf"),
            filetype=DocumentType.PDF, size_bytes=100,
        )
        assert document_repo.delete(db_conn, doc.id) is True
        assert document_repo.get_by_id(db_conn, doc.id) is None

    def test_count_by_project(self, db_conn, document_repo, sample_project_id) -> None:
        """count_by_project() should return correct count."""
        assert document_repo.count_by_project(db_conn, sample_project_id) == 0
        document_repo.create(
            db_conn, project_id=sample_project_id,
            filename="c.pdf", filepath=Path("/c.pdf"),
            filetype=DocumentType.PDF, size_bytes=100,
        )
        assert document_repo.count_by_project(db_conn, sample_project_id) == 1


class TestConversationRepository:
    """Tests for conversation, message, and pinned fact operations."""

    def test_create_conversation(self, db_conn, conversation_repo, sample_project_id) -> None:
        """create() should return a Conversation."""
        conv = conversation_repo.create(db_conn, sample_project_id, "Test Chat")
        assert conv.title == "Test Chat"
        assert conv.project_id == sample_project_id

    def test_add_and_get_messages(self, db_conn, conversation_repo, sample_project_id) -> None:
        """add_message() and get_messages() should round-trip correctly."""
        conv = conversation_repo.create(db_conn, sample_project_id, "Msg Test")
        conversation_repo.add_message(
            db_conn, conv.id, MessageRole.USER, "What processor?"
        )
        conversation_repo.add_message(
            db_conn, conv.id, MessageRole.ASSISTANT, "STM32F407",
            confidence_score=85.0,
        )
        messages = conversation_repo.get_messages(db_conn, conv.id)
        assert len(messages) == 2
        assert messages[0].role == MessageRole.USER
        assert messages[1].confidence_score == 85.0

    def test_get_by_id_includes_messages(self, db_conn, conversation_repo, sample_project_id) -> None:
        """get_by_id() should include messages and pinned facts."""
        conv = conversation_repo.create(db_conn, sample_project_id, "Full Load")
        conversation_repo.add_message(db_conn, conv.id, MessageRole.USER, "Hello")
        loaded = conversation_repo.get_by_id(db_conn, conv.id)
        assert loaded is not None
        assert len(loaded.messages) == 1

    def test_list_by_project(self, db_conn, conversation_repo, sample_project_id) -> None:
        """list_by_project() should return conversations without messages."""
        conversation_repo.create(db_conn, sample_project_id, "Conv A")
        conversation_repo.create(db_conn, sample_project_id, "Conv B")
        convs = conversation_repo.list_by_project(db_conn, sample_project_id)
        assert len(convs) == 2

    def test_update_summary(self, db_conn, conversation_repo, sample_project_id) -> None:
        """update_summary() should set the conversation summary."""
        conv = conversation_repo.create(db_conn, sample_project_id, "Summary Test")
        conversation_repo.update_summary(db_conn, conv.id, "Discussed board components")
        loaded = conversation_repo.get_by_id(db_conn, conv.id)
        assert loaded is not None
        assert loaded.summary == "Discussed board components"

    def test_delete_conversation(self, db_conn, conversation_repo, sample_project_id) -> None:
        """delete() should remove the conversation."""
        conv = conversation_repo.create(db_conn, sample_project_id, "To Delete")
        assert conversation_repo.delete(db_conn, conv.id) is True
        assert conversation_repo.get_by_id(db_conn, conv.id) is None

    def test_pinned_facts(self, db_conn, conversation_repo, sample_project_id) -> None:
        """add_pinned_fact() and get_pinned_facts() should round-trip."""
        conv = conversation_repo.create(db_conn, sample_project_id, "Pins")
        fact = conversation_repo.add_pinned_fact(
            db_conn, conv.id, "Main CPU is STM32F407"
        )
        facts = conversation_repo.get_pinned_facts(db_conn, conv.id)
        assert len(facts) == 1
        assert facts[0].content == "Main CPU is STM32F407"
