"""Fixtures for ingestion tests."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from tests.fixtures.create_fixtures import (
    create_sample_c,
    create_sample_csv,
    create_sample_image,
    create_sample_pdf,
    create_sample_txt,
)


@pytest.fixture
def fixtures_dir(tmp_path: Path) -> Path:
    """Temporary directory for test fixture files."""
    d = tmp_path / "fixtures"
    d.mkdir()
    return d


@pytest.fixture
def sample_pdf(fixtures_dir: Path) -> Path:
    return create_sample_pdf(fixtures_dir)


@pytest.fixture
def sample_image(fixtures_dir: Path) -> Path:
    return create_sample_image(fixtures_dir)


@pytest.fixture
def sample_c(fixtures_dir: Path) -> Path:
    return create_sample_c(fixtures_dir)


@pytest.fixture
def sample_txt(fixtures_dir: Path) -> Path:
    return create_sample_txt(fixtures_dir)


@pytest.fixture
def sample_csv(fixtures_dir: Path) -> Path:
    return create_sample_csv(fixtures_dir)


@pytest.fixture
def mock_embedder() -> MagicMock:
    """Mock embedder returning 768-dim vectors."""
    mock = MagicMock()
    mock.embed_chunks.side_effect = lambda chunks, **kw: [[0.1] * 768 for _ in chunks]
    return mock
