"""Plain text, Markdown, HTML, and structured text parser."""

import re
from pathlib import Path

from core.ingest.parsers.base import BaseParser, PageContent, ParseResult
from core.logging import get_logger

log = get_logger(__name__)

_ENCODINGS_TO_TRY = ("utf-8", "latin-1", "cp1252", "ascii")


class TextParser(BaseParser):
    """Parse plain text, Markdown, HTML, XML, and JSON files."""

    def parse(self, filepath: Path) -> ParseResult:
        """Parse a text-based file, handling encoding detection and format cleanup.

        Args:
            filepath: Path to the text file.

        Returns:
            ParseResult with cleaned text content and metadata.
        """
        warnings: list[str] = []
        raw_text, encoding = self._read_with_encoding(filepath, warnings)

        if raw_text is None:
            return ParseResult(text_content="", warnings=warnings)

        ext = filepath.suffix.lower()
        metadata = {
            "encoding": encoding,
            "line_count": raw_text.count("\n") + 1,
            "char_count": len(raw_text),
            "format": ext.lstrip("."),
        }

        # Format-specific processing
        if ext in (".html", ".htm"):
            text_content = self._parse_html(raw_text)
        elif ext == ".md":
            text_content = self._parse_markdown(raw_text)
        elif ext in (".xml",):
            text_content = raw_text  # Keep XML as-is for search
        elif ext == ".json":
            text_content = raw_text  # Keep JSON as-is
        else:
            text_content = raw_text

        # Build page-like structure from section headings
        pages = self._extract_sections(text_content)

        log.info("text_parsed", filepath=str(filepath), encoding=encoding, chars=len(text_content))
        return ParseResult(
            text_content=text_content, pages=pages, metadata=metadata, warnings=warnings,
        )

    def _read_with_encoding(
        self, filepath: Path, warnings: list[str]
    ) -> tuple[str | None, str]:
        """Try multiple encodings to read the file."""
        for enc in _ENCODINGS_TO_TRY:
            try:
                text = filepath.read_text(encoding=enc)
                return text, enc
            except (UnicodeDecodeError, ValueError):
                continue

        # Last resort: read with replacement
        try:
            text = filepath.read_text(encoding="utf-8", errors="replace")
            warnings.append("File encoding uncertain, read with replacement characters.")
            return text, "utf-8-replace"
        except Exception as e:
            warnings.append(f"Failed to read file: {e}")
            return None, "unknown"

    def _parse_html(self, raw: str) -> str:
        """Strip HTML tags, preserving heading structure."""
        # Remove script and style blocks
        text = re.sub(r"<script[^>]*>.*?</script>", "", raw, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<style[^>]*>.*?</style>", "", raw, flags=re.DOTALL | re.IGNORECASE)

        # Convert headings to section markers
        for level in range(1, 7):
            text = re.sub(
                rf"<h{level}[^>]*>(.*?)</h{level}>",
                rf"\n{'#' * level} \1\n",
                text,
                flags=re.DOTALL | re.IGNORECASE,
            )

        # Convert <br>, <p>, <li> to newlines
        text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"</?p[^>]*>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"<li[^>]*>", "\n- ", text, flags=re.IGNORECASE)

        # Strip remaining tags
        text = re.sub(r"<[^>]+>", "", text)

        # Unescape common HTML entities manually (avoid html.entities on Python 3.14)
        for entity, char in [("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
                              ("&quot;", '"'), ("&#39;", "'"), ("&nbsp;", " ")]:
            text = text.replace(entity, char)

        # Clean up whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _parse_markdown(self, raw: str) -> str:
        """Lightly clean Markdown, preserving headers as section markers."""
        # Markdown is already quite readable — just normalize whitespace
        return re.sub(r"\n{3,}", "\n\n", raw).strip()

    def _extract_sections(self, text: str) -> list[PageContent]:
        """Split text into page-like sections based on headings."""
        sections: list[PageContent] = []
        # Split on markdown-style headings
        parts = re.split(r"^(#{1,6}\s+.+)$", text, flags=re.MULTILINE)

        current_heading = ""
        current_text_parts: list[str] = []

        for part in parts:
            if re.match(r"^#{1,6}\s+", part):
                if current_text_parts:
                    sections.append(PageContent(
                        page_number=len(sections) + 1,
                        text="\n".join(current_text_parts).strip(),
                    ))
                current_heading = part.strip()
                current_text_parts = [current_heading]
            else:
                current_text_parts.append(part)

        # Final section
        if current_text_parts:
            sections.append(PageContent(
                page_number=len(sections) + 1,
                text="\n".join(current_text_parts).strip(),
            ))

        # If no sections found, treat entire text as one page
        if not sections and text.strip():
            sections.append(PageContent(page_number=1, text=text.strip()))

        return sections
