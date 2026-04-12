"""Tests for the health check API endpoint.

Note: Requires Python < 3.14 or a patched starlette due to html.entities
stdlib regression in CPython 3.14.x. Tests are skipped when the import fails.
"""

import sys
from unittest.mock import MagicMock

import pytest

# Guard against Python 3.14 html.entities breakage at import time
try:
    from fastapi.testclient import TestClient

    _HAS_TESTCLIENT = True
except (ImportError, ModuleNotFoundError):
    _HAS_TESTCLIENT = False

pytestmark = pytest.mark.skipif(
    not _HAS_TESTCLIENT,
    reason="FastAPI TestClient unavailable (Python 3.14 html.entities issue)",
)


@pytest.fixture
def client(tmp_path):
    """Create a test client with mocked dependencies."""
    from backend.config import Settings
    from core.database.connection import DatabaseManager
    from core.vector_store.chroma_client import ChromaVectorStore

    # Real database in temp dir
    db_path = tmp_path / "test.db"
    db_manager = DatabaseManager(db_path=db_path)
    db_manager.initialize()

    # Real vector store in temp dir
    chroma_path = tmp_path / "chroma"
    chroma_path.mkdir()
    vs = ChromaVectorStore(persist_directory=chroma_path)

    # Mock Ollama client
    mock_ollama = MagicMock()
    mock_ollama.health_check.return_value = False
    mock_ollama.list_models.return_value = []

    # Override dependencies
    from backend import dependencies
    from backend.main import app

    app.dependency_overrides[dependencies.get_db] = lambda: db_manager
    app.dependency_overrides[dependencies.get_vector_store] = lambda: vs
    app.dependency_overrides[dependencies.get_ollama_client] = lambda: mock_ollama

    with TestClient(app) as tc:
        yield tc

    app.dependency_overrides.clear()
    db_manager.close()


class TestHealthEndpoint:
    """Tests for GET /api/v1/health."""

    def test_health_returns_200(self, client) -> None:
        """Health endpoint should return 200 even when Ollama is down."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200

    def test_health_response_structure(self, client) -> None:
        """Health response should contain all required fields."""
        data = client.get("/api/v1/health").json()
        assert "status" in data
        assert "ollama_connected" in data
        assert "database_ok" in data
        assert "vector_store_ok" in data
        assert "document_count" in data
        assert "available_models" in data

    def test_health_degraded_without_ollama(self, client) -> None:
        """Status should be 'degraded' when Ollama is not running."""
        data = client.get("/api/v1/health").json()
        assert data["status"] == "degraded"
        assert data["ollama_connected"] is False
        assert data["database_ok"] is True
        assert data["vector_store_ok"] is True
