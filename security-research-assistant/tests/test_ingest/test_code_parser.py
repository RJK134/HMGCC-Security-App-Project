"""Tests for code parser with tree-sitter."""

from pathlib import Path

from core.ingest.parsers.code_parser import CodeParser


class TestCodeParser:
    """Tests for CodeParser."""

    def test_parse_c_file(self, sample_c: Path) -> None:
        """Parser should extract content from a C file."""
        result = CodeParser().parse(sample_c)
        assert "gpio_init" in result.text_content
        assert "gpio_read" in result.text_content
        assert "gpio_write" in result.text_content

    def test_parse_c_extracts_structs(self, sample_c: Path) -> None:
        """Parser should extract struct definitions."""
        result = CodeParser().parse(sample_c)
        assert "gpio_config_t" in result.text_content or "pin_number" in result.text_content

    def test_parse_c_extracts_includes(self, sample_c: Path) -> None:
        """Parser should extract include statements."""
        result = CodeParser().parse(sample_c)
        assert "stdint.h" in result.text_content

    def test_parse_c_metadata(self, sample_c: Path) -> None:
        """Metadata should include language and line count."""
        result = CodeParser().parse(sample_c)
        assert result.metadata["language"] == "c"
        assert result.metadata["line_count"] > 0

    def test_parse_python_file(self, tmp_path: Path) -> None:
        """Parser should handle Python files."""
        py = tmp_path / "test.py"
        py.write_text('def hello():\n    """Say hello."""\n    print("hello")\n')
        result = CodeParser().parse(py)
        assert "hello" in result.text_content
        assert result.metadata["language"] == "python"

    def test_parse_unsupported_language(self, tmp_path: Path) -> None:
        """Parser should fall back to raw text for unsupported languages."""
        asm = tmp_path / "boot.asm"
        asm.write_text("MOV AX, 0x1234\nINT 0x21\n")
        result = CodeParser().parse(asm)
        assert "MOV AX" in result.text_content
        assert result.metadata["language"] == "asm"

    def test_parse_empty_file(self, tmp_path: Path) -> None:
        """Parser should handle empty code files."""
        empty = tmp_path / "empty.c"
        empty.write_text("")
        result = CodeParser().parse(empty)
        assert result.text_content is not None
