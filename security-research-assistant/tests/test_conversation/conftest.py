"""Fixtures for conversation tests."""

from pathlib import Path
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from core.conversation.manager import ConversationManager
from core.conversation.memory import MemoryManager
from core.conversation.summariser import ConversationSummariser
from core.database.connection import DatabaseManager
from core.database.repositories.project_repo import ProjectRepository


@pytest.fixture
def conv_db(tmp_path: Path) -> DatabaseManager:
    """Database for conversation tests."""
    db = DatabaseManager(tmp_path / "conv_test.db")
    db.initialize()
    return db


@pytest.fixture
def conv_project_id(conv_db: DatabaseManager):
    """Create a test project, return its ID."""
    repo = ProjectRepository()
    project = repo.create(conv_db.get_connection(), "Conversation Test Project")
    return project.id


@pytest.fixture
def mock_summariser() -> MagicMock:
    """Mock summariser returning predetermined responses."""
    mock = MagicMock(spec=ConversationSummariser)
    mock.summarise_conversation.return_value = "Summary: Discussed processor specifications and GPIO pins."
    mock.extract_key_facts.return_value = [
        "Main processor is STM32F407VGT6",
        "Operating voltage is 3.3V",
        "SPI1 uses PA5, PA6, PA7",
    ]
    return mock


@pytest.fixture
def conv_manager(conv_db: DatabaseManager, mock_summariser) -> ConversationManager:
    """ConversationManager with mock summariser."""
    return ConversationManager(conv_db, mock_summariser)


@pytest.fixture
def memory_manager(conv_db: DatabaseManager) -> MemoryManager:
    """MemoryManager for tests."""
    return MemoryManager(conv_db)
