"""Tests for report generator."""

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from core.database.connection import DatabaseManager
from core.database.repositories.project_repo import ProjectRepository
from core.reports.generator import ReportGenerator
from core.reports.templates import ReportType


@pytest.fixture
def report_db(tmp_path: Path):
    db = DatabaseManager(tmp_path / "report.db")
    db.initialize()
    conn = db.get_connection()
    project_id = uuid4()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO projects (id, name, created_at, updated_at) VALUES (?, ?, ?, ?)",
        (str(project_id), "Report Test", now, now),
    )
    doc_id = uuid4()
    conn.execute(
        "INSERT INTO documents (id, project_id, filename, filepath, filetype, "
        "size_bytes, status, source_tier, import_timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (str(doc_id), str(project_id), "datasheet.pdf", "/ds.pdf", "pdf",
         5000, "indexed", "tier_1_manufacturer", now),
    )
    conn.execute(
        "INSERT INTO chunks (id, document_id, content, chunk_index, page_number, "
        "section_heading, token_count, chroma_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (str(uuid4()), str(doc_id), "STM32F407 runs at 168 MHz with SPI and I2C.",
         0, 1, "Overview", 20, f"{doc_id}_0"),
    )
    conn.commit()
    return db, project_id


class TestReportGenerator:
    def test_generate_product_overview(self, report_db) -> None:
        db, project_id = report_db
        mock_llm = MagicMock()
        mock_llm.generate.return_value = "This is a test section about the product."
        gen = ReportGenerator(db, mock_llm)
        report = gen.generate_report(project_id, ReportType.PRODUCT_OVERVIEW)
        assert report.title == "Product Overview Report"
        assert len(report.sections) >= 6

    def test_generate_investigation_summary(self, report_db) -> None:
        db, project_id = report_db
        mock_llm = MagicMock()
        mock_llm.generate.return_value = "Investigation findings section."
        gen = ReportGenerator(db, mock_llm)
        report = gen.generate_report(project_id, ReportType.INVESTIGATION_SUMMARY)
        assert "Investigation" in report.title
        assert len(report.sections) >= 5

    def test_generate_empty_project(self, tmp_path) -> None:
        db = DatabaseManager(tmp_path / "empty.db")
        db.initialize()
        conn = db.get_connection()
        pid = uuid4()
        now = datetime.now(timezone.utc).isoformat()
        conn.execute("INSERT INTO projects (id, name, created_at, updated_at) VALUES (?, ?, ?, ?)",
                     (str(pid), "Empty", now, now))
        conn.commit()
        mock_llm = MagicMock()
        mock_llm.generate.return_value = "No data available for this section."
        gen = ReportGenerator(db, mock_llm)
        report = gen.generate_report(pid, ReportType.PRODUCT_OVERVIEW)
        assert len(report.sections) > 0

    def test_report_stored_in_db(self, report_db) -> None:
        db, project_id = report_db
        mock_llm = MagicMock()
        mock_llm.generate.return_value = "Content."
        gen = ReportGenerator(db, mock_llm)
        report = gen.generate_report(project_id, ReportType.SYSTEM_ARCHITECTURE)
        conn = db.get_connection()
        row = conn.execute("SELECT * FROM reports WHERE id = ?", (str(report.id),)).fetchone()
        assert row is not None

    def test_metadata_populated(self, report_db) -> None:
        db, project_id = report_db
        mock_llm = MagicMock()
        mock_llm.generate.return_value = "Content."
        gen = ReportGenerator(db, mock_llm)
        report = gen.generate_report(project_id, ReportType.PRODUCT_OVERVIEW)
        assert "generation_time_seconds" in report.metadata
        assert "llm_calls" in report.metadata
