"""Tests for image parser with OCR."""

from pathlib import Path

import pytest

from core.ingest.parsers.image_parser import ImageParser


def _tesseract_available() -> bool:
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


class TestImageParser:
    """Tests for ImageParser."""

    def test_parse_returns_result(self, sample_image: Path) -> None:
        """Parser should return a ParseResult without crashing."""
        result = ImageParser().parse(sample_image)
        assert result is not None
        assert result.metadata.get("width") == 400
        assert result.metadata.get("height") == 200

    def test_parse_stores_image_bytes(self, sample_image: Path) -> None:
        """Parser should store original image bytes."""
        result = ImageParser().parse(sample_image)
        assert len(result.images) == 1
        assert len(result.images[0].image_bytes) > 0

    def test_parse_invalid_image(self, tmp_path: Path) -> None:
        """Parser should handle non-image files gracefully."""
        bad = tmp_path / "bad.png"
        bad.write_text("not an image")
        result = ImageParser().parse(bad)
        assert len(result.warnings) > 0

    @pytest.mark.skipif(
        not _tesseract_available(),
        reason="Tesseract not installed",
    )
    def test_ocr_extracts_text(self, sample_image: Path) -> None:
        """OCR should extract text from the test image."""
        result = ImageParser().parse(sample_image)
        assert result.text_content  # Non-empty string
