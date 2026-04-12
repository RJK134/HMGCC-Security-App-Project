"""Tests for file type detection."""

from pathlib import Path

import pytest

from core.exceptions import DocumentProcessingError
from core.ingest.detector import detect_file_type
from core.models.document import DocumentType


class TestDetectFileType:
    """Tests for detect_file_type()."""

    def test_pdf_detection(self, sample_pdf: Path) -> None:
        assert detect_file_type(sample_pdf) == DocumentType.PDF

    def test_image_detection(self, sample_image: Path) -> None:
        assert detect_file_type(sample_image) == DocumentType.IMAGE

    def test_code_detection(self, sample_c: Path) -> None:
        assert detect_file_type(sample_c) == DocumentType.CODE

    def test_text_detection(self, sample_txt: Path) -> None:
        assert detect_file_type(sample_txt) == DocumentType.TEXT

    def test_csv_detection(self, sample_csv: Path) -> None:
        assert detect_file_type(sample_csv) == DocumentType.SPREADSHEET

    def test_unsupported_extension(self, tmp_path: Path) -> None:
        f = tmp_path / "test.xyz"
        f.write_text("data")
        with pytest.raises(DocumentProcessingError, match="Unsupported"):
            detect_file_type(f)

    def test_nonexistent_file(self, tmp_path: Path) -> None:
        with pytest.raises(DocumentProcessingError, match="not found"):
            detect_file_type(tmp_path / "nonexistent.pdf")

    def test_python_detection(self, tmp_path: Path) -> None:
        f = tmp_path / "script.py"
        f.write_text("print('hello')")
        assert detect_file_type(f) == DocumentType.CODE

    def test_html_detection(self, tmp_path: Path) -> None:
        f = tmp_path / "page.html"
        f.write_text("<html><body>test</body></html>")
        assert detect_file_type(f) == DocumentType.TEXT

    def test_markdown_detection(self, tmp_path: Path) -> None:
        f = tmp_path / "readme.md"
        f.write_text("# Title\nContent")
        assert detect_file_type(f) == DocumentType.TEXT
