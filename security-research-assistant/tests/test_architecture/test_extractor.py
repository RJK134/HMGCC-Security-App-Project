"""Tests for architecture component extraction."""

from pathlib import Path
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from core.architecture.extractor import ArchitectureExtractor
from core.database.connection import DatabaseManager
from core.database.repositories.project_repo import ProjectRepository


@pytest.fixture
def arch_db(tmp_path: Path):
    """Database with project and sample chunks for architecture extraction."""
    db = DatabaseManager(tmp_path / "arch.db")
    db.initialize()
    conn = db.get_connection()

    # Create project
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    project_id = uuid4()
    conn.execute(
        "INSERT INTO projects (id, name, created_at, updated_at) VALUES (?, ?, ?, ?)",
        (str(project_id), "Arch Test", now, now),
    )
    doc_id = uuid4()
    conn.execute(
        "INSERT INTO documents (id, project_id, filename, filepath, filetype, "
        "size_bytes, status, source_tier, import_timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (str(doc_id), str(project_id), "datasheet.pdf", "/data/ds.pdf", "pdf",
         1000, "indexed", "tier_1_manufacturer", now),
    )
    conn.execute(
        "INSERT INTO chunks (id, document_id, content, chunk_index, page_number, "
        "section_heading, token_count, chroma_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (str(uuid4()), str(doc_id),
         "The STM32F407 processor uses SPI, I2C, and UART interfaces. "
         "It communicates via Modbus RTU over RS-485. The firmware runs FreeRTOS.",
         0, 1, "Overview", 30, f"{doc_id}_0"),
    )
    conn.commit()
    return db, project_id


class TestArchitectureExtractor:
    def test_extract_returns_result(self, arch_db) -> None:
        db, project_id = arch_db
        mock_llm = MagicMock()
        mock_llm.generate.return_value = (
            "COMPONENT: STM32F407 | processor | Main MCU\n"
            "INTERFACE: SPI | STM32F407 | Sensor Array\n"
            "PROTOCOL: Modbus RTU | application | Industrial protocol\n"
            "SOFTWARE: FreeRTOS | os | v10.4\n"
        )
        extractor = ArchitectureExtractor(db, mock_llm)
        result = extractor.extract(project_id)
        assert len(result.components) >= 1
        assert result.components[0].name == "STM32F407"
        assert len(result.interfaces) >= 1
        assert len(result.protocols) >= 1
        assert len(result.software) >= 1

    def test_extract_empty_project(self, tmp_path) -> None:
        db = DatabaseManager(tmp_path / "empty.db")
        db.initialize()
        mock_llm = MagicMock()
        extractor = ArchitectureExtractor(db, mock_llm)
        result = extractor.extract(uuid4())
        assert len(result.warnings) > 0

    def test_extract_deduplicates(self, arch_db) -> None:
        db, project_id = arch_db
        mock_llm = MagicMock()
        mock_llm.generate.return_value = (
            "COMPONENT: STM32F407 | processor | MCU\n"
            "COMPONENT: STM32F407 | processor | Main processor\n"
        )
        extractor = ArchitectureExtractor(db, mock_llm)
        result = extractor.extract(project_id)
        assert len(result.components) == 1

    def test_extract_handles_llm_failure(self, arch_db) -> None:
        db, project_id = arch_db
        mock_llm = MagicMock()
        mock_llm.generate.side_effect = RuntimeError("LLM down")
        extractor = ArchitectureExtractor(db, mock_llm)
        result = extractor.extract(project_id)
        assert len(result.warnings) > 0
