"""Tests for text, markdown, and HTML parser."""

from pathlib import Path

from core.ingest.parsers.text_parser import TextParser


class TestTextParser:
    """Tests for TextParser."""

    def test_parse_plain_text(self, sample_txt: Path) -> None:
        """Parser should read plain text with sections."""
        result = TextParser().parse(sample_txt)
        assert "Modbus RTU" in result.text_content
        assert "STM32F407" in result.text_content

    def test_parse_preserves_headings(self, sample_txt: Path) -> None:
        """Parser should preserve heading structure."""
        result = TextParser().parse(sample_txt)
        assert "Communication Protocols" in result.text_content
        assert "Hardware Architecture" in result.text_content

    def test_parse_sections_as_pages(self, sample_txt: Path) -> None:
        """Parser should split into page-like sections by headings."""
        result = TextParser().parse(sample_txt)
        assert len(result.pages) >= 2  # At least a few sections

    def test_parse_html(self, tmp_path: Path) -> None:
        """Parser should strip HTML tags and preserve text."""
        f = tmp_path / "test.html"
        f.write_text("<html><body><h1>Title</h1><p>Content here.</p></body></html>")
        result = TextParser().parse(f)
        assert "Title" in result.text_content
        assert "Content here" in result.text_content
        assert "<html>" not in result.text_content

    def test_parse_markdown(self, tmp_path: Path) -> None:
        """Parser should preserve markdown headings."""
        f = tmp_path / "test.md"
        f.write_text("# Header One\n\nSome text.\n\n## Header Two\n\nMore text.\n")
        result = TextParser().parse(f)
        assert "Header One" in result.text_content
        assert "Header Two" in result.text_content

    def test_parse_encoding_fallback(self, tmp_path: Path) -> None:
        """Parser should handle non-UTF-8 encodings."""
        f = tmp_path / "latin.txt"
        f.write_bytes("Stra\xdfe in M\xfcnchen".encode("latin-1"))
        result = TextParser().parse(f)
        assert "Stra" in result.text_content

    def test_parse_metadata(self, sample_txt: Path) -> None:
        """Metadata should include encoding and line count."""
        result = TextParser().parse(sample_txt)
        assert result.metadata["encoding"] == "utf-8"
        assert result.metadata["line_count"] > 0
