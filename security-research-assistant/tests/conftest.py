"""Shared pytest fixtures for the Security Research Assistant test suite."""

import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from core.database.connection import DatabaseManager
from core.database.repositories.conversation_repo import ConversationRepository
from core.database.repositories.document_repo import DocumentRepository
from core.database.repositories.project_repo import ProjectRepository


@pytest.fixture
def tmp_dir(tmp_path: Path) -> Path:
    """Provide a temporary directory for test data."""
    return tmp_path


@pytest.fixture
def db_manager(tmp_dir: Path) -> DatabaseManager:
    """Provide an initialised DatabaseManager using a temp database file."""
    db_path = tmp_dir / "test.db"
    manager = DatabaseManager(db_path=db_path)
    manager.initialize()
    return manager


@pytest.fixture
def db_conn(db_manager: DatabaseManager) -> sqlite3.Connection:
    """Provide an open database connection."""
    return db_manager.get_connection()


@pytest.fixture
def project_repo() -> ProjectRepository:
    """Provide a ProjectRepository instance."""
    return ProjectRepository()


@pytest.fixture
def document_repo() -> DocumentRepository:
    """Provide a DocumentRepository instance."""
    return DocumentRepository()


@pytest.fixture
def conversation_repo() -> ConversationRepository:
    """Provide a ConversationRepository instance."""
    return ConversationRepository()


@pytest.fixture
def sample_project_id(db_conn: sqlite3.Connection, project_repo: ProjectRepository):
    """Create a sample project and return its ID."""
    project = project_repo.create(db_conn, name="Test Project", description="For testing")
    return project.id


@pytest.fixture
def chroma_dir(tmp_dir: Path) -> Path:
    """Provide a temporary directory for ChromaDB storage."""
    chroma_path = tmp_dir / "chroma"
    chroma_path.mkdir()
    return chroma_path


@pytest.fixture
def mock_ollama() -> MagicMock:
    """Provide a mock OllamaClient that doesn't need a running Ollama server."""
    mock = MagicMock()
    mock.health_check.return_value = False
    mock.list_models.return_value = []
    mock.generate.return_value = "Mock LLM response"
    mock.generate_embedding.return_value = [0.1] * 384
    return mock
