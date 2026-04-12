"""Tests for PDF parser."""

import sys
from pathlib import Path

import pytest

# PyMuPDF imports html.entities internally, broken on Python 3.14
pytestmark = pytest.mark.skipif(
    sys.version_info >= (3, 14),
    reason="PyMuPDF depends on html.entities, broken in Python 3.14",
)

from core.ingest.parsers.pdf_parser import PdfParser


class TestPdfParser:
    """Tests for PdfParser."""

    def test_parse_extracts_text(self, sample_pdf: Path) -> None:
        """Parser should extract readable text from PDF."""
        result = PdfParser().parse(sample_pdf)
        assert "STM32F407" in result.text_content
        assert "ARM Cortex-M4" in result.text_content

    def test_parse_multi_page(self, sample_pdf: Path) -> None:
        """Parser should return content from all pages."""
        result = PdfParser().parse(sample_pdf)
        assert len(result.pages) == 3
        assert "Pin Configuration" in result.pages[1].text

    def test_parse_metadata(self, sample_pdf: Path) -> None:
        """Parser should capture page count in metadata."""
        result = PdfParser().parse(sample_pdf)
        assert result.metadata["page_count"] == 3

    def test_parse_corrupted_pdf(self, tmp_path: Path) -> None:
        """Parser should handle corrupted PDFs gracefully."""
        bad = tmp_path / "bad.pdf"
        bad.write_bytes(b"not a real pdf content here")
        result = PdfParser().parse(bad)
        assert len(result.warnings) > 0
        assert result.text_content == ""

    def test_parse_empty_pdf(self, tmp_path: Path) -> None:
        """Parser should handle a minimal/empty PDF."""
        from reportlab.pdfgen import canvas
        f = tmp_path / "empty.pdf"
        c = canvas.Canvas(str(f))
        c.showPage()
        c.save()
        result = PdfParser().parse(f)
        assert result.metadata["page_count"] == 1
