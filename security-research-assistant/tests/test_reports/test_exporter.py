"""Tests for report exporter — Markdown, PDF, JSON, HTML."""

import json
import sys
from pathlib import Path
from uuid import uuid4

import pytest

from core.reports.exporter import ReportExporter
from core.reports.templates import Report, ReportSection, ReportType


def _make_report() -> Report:
    return Report(
        project_id=uuid4(),
        report_type=ReportType.PRODUCT_OVERVIEW,
        title="Test Product Overview",
        sections=[
            ReportSection(heading="Executive Summary", content="This product is an ICS controller."),
            ReportSection(heading="Components", content="STM32F407 processor [Source: datasheet.pdf, Page 1]."),
            ReportSection(heading="Gaps", content="Firmware not available.", confidence_note="Low confidence: missing firmware data."),
        ],
        metadata={"generation_time_seconds": 5.2, "llm_calls": 3},
    )


class TestReportExporter:
    def setup_method(self) -> None:
        self.exporter = ReportExporter()
        self.report = _make_report()

    def test_export_markdown(self) -> None:
        md = self.exporter.export_markdown(self.report)
        assert "# Test Product Overview" in md
        assert "## Executive Summary" in md
        assert "STM32F407" in md
        assert "Low confidence" in md

    @pytest.mark.skipif(sys.version_info >= (3, 14), reason="reportlab html.entities issue on Python 3.14")
    def test_export_pdf(self, tmp_path: Path) -> None:
        out = tmp_path / "test.pdf"
        result = self.exporter.export_pdf(self.report, out)
        assert result.exists()
        assert result.stat().st_size > 0
        with open(result, "rb") as f:
            assert f.read(4) == b"%PDF"

    def test_export_json(self) -> None:
        j = self.exporter.export_json(self.report)
        parsed = json.loads(j)
        assert parsed["title"] == "Test Product Overview"
        assert len(parsed["sections"]) == 3

    def test_export_html(self) -> None:
        html = self.exporter.export_html(self.report)
        assert "<html" in html
        assert "Test Product Overview" in html
        assert "STM32F407" in html
        assert "Low confidence" in html
