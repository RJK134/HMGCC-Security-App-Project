"""Code parser using tree-sitter for structural extraction of source files."""

from pathlib import Path

from core.ingest.parsers.base import BaseParser, ParseResult
from core.logging import get_logger

log = get_logger(__name__)

# Extension to tree-sitter language mapping
_LANGUAGE_MAP: dict[str, str] = {
    ".c": "c", ".h": "c", ".cpp": "c", ".cc": "c", ".hpp": "c",
    ".py": "python",
}

# Extensions that are code but lack tree-sitter support — use raw text
_RAW_CODE_EXTENSIONS = {".asm", ".s", ".rs", ".go", ".java", ".sh", ".js", ".ts"}


class CodeParser(BaseParser):
    """Parse source code files extracting functions, structs, and comments."""

    def parse(self, filepath: Path) -> ParseResult:
        """Parse a code file, extracting structural elements where possible.

        Uses tree-sitter for C and Python files. Falls back to raw text
        with basic heuristics for other languages.

        Args:
            filepath: Path to the source code file.

        Returns:
            ParseResult with structured code representation.
        """
        warnings: list[str] = []

        try:
            raw_text = filepath.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            warnings.append(f"Failed to read file: {e}")
            return ParseResult(text_content="", warnings=warnings)

        ext = filepath.suffix.lower()
        language = _LANGUAGE_MAP.get(ext)
        line_count = raw_text.count("\n") + 1

        metadata: dict = {
            "language": language or ext.lstrip("."),
            "line_count": line_count,
            "file_size": filepath.stat().st_size,
        }

        # Try tree-sitter structured parsing
        if language:
            structured = self._parse_with_tree_sitter(raw_text, language, warnings)
            if structured:
                metadata["function_count"] = structured.get("function_count", 0)
                metadata["includes"] = structured.get("includes", [])
                text_content = structured.get("text", raw_text)
                log.info(
                    "code_parsed_structured",
                    filepath=str(filepath),
                    language=language,
                    functions=metadata["function_count"],
                )
                return ParseResult(
                    text_content=text_content, metadata=metadata, warnings=warnings,
                )

        # Fallback: raw text with basic annotation
        text_content = f"[Source: {filepath.name} | Language: {metadata['language']} | Lines: {line_count}]\n\n{raw_text}"
        log.info("code_parsed_raw", filepath=str(filepath), language=metadata["language"])
        return ParseResult(text_content=text_content, metadata=metadata, warnings=warnings)

    def _parse_with_tree_sitter(
        self, source: str, language: str, warnings: list[str]
    ) -> dict | None:
        """Attempt tree-sitter parsing to extract structural elements.

        Returns a dict with 'text', 'function_count', 'includes', or None on failure.
        """
        try:
            import tree_sitter_c
            import tree_sitter_python
            from tree_sitter import Language, Parser

            lang_modules = {"c": tree_sitter_c, "python": tree_sitter_python}
            lang_mod = lang_modules.get(language)
            if not lang_mod:
                return None

            lang = Language(lang_mod.language())
            parser = Parser(lang)
            tree = parser.parse(source.encode("utf-8"))
            root = tree.root_node

            functions = self._extract_functions(root, source, language)
            includes = self._extract_includes(root, source, language)
            structs = self._extract_structs(root, source, language)
            comments = self._extract_top_comments(root, source)

            # Build structured text representation
            parts: list[str] = []
            if comments:
                parts.append(f"[File Comments]\n{comments}")
            if includes:
                parts.append(f"[Includes/Imports]\n" + "\n".join(includes))
            if structs:
                parts.append(f"[Structs/Classes]\n" + "\n\n".join(structs))
            for fn in functions:
                parts.append(fn)

            # Also append the raw source for full-text search
            parts.append(f"\n[Full Source]\n{source}")

            return {
                "text": "\n\n".join(parts),
                "function_count": len(functions),
                "includes": includes,
            }

        except ImportError:
            warnings.append(f"tree-sitter language module for '{language}' not available.")
            return None
        except Exception as e:
            warnings.append(f"tree-sitter parsing failed: {e}")
            return None

    def _extract_functions(self, root, source: str, language: str) -> list[str]:
        """Extract function definitions from the syntax tree."""
        functions: list[str] = []
        if language == "c":
            node_type = "function_definition"
        elif language == "python":
            node_type = "function_definition"
        else:
            return functions

        for node in self._find_nodes(root, node_type):
            text = source[node.start_byte:node.end_byte]
            # Truncate very long function bodies
            lines = text.split("\n")
            if len(lines) > 20:
                header = "\n".join(lines[:15])
                functions.append(f"[Function]\n{header}\n  ... ({len(lines)} lines total)")
            else:
                functions.append(f"[Function]\n{text}")
        return functions

    def _extract_includes(self, root, source: str, language: str) -> list[str]:
        """Extract include/import statements."""
        includes: list[str] = []
        if language == "c":
            for node in self._find_nodes(root, "preproc_include"):
                includes.append(source[node.start_byte:node.end_byte].strip())
        elif language == "python":
            for ntype in ("import_statement", "import_from_statement"):
                for node in self._find_nodes(root, ntype):
                    includes.append(source[node.start_byte:node.end_byte].strip())
        return includes

    def _extract_structs(self, root, source: str, language: str) -> list[str]:
        """Extract struct/class definitions."""
        structs: list[str] = []
        if language == "c":
            for node in self._find_nodes(root, "struct_specifier"):
                text = source[node.start_byte:node.end_byte]
                structs.append(f"[Struct]\n{text}")
        elif language == "python":
            for node in self._find_nodes(root, "class_definition"):
                text = source[node.start_byte:node.end_byte]
                lines = text.split("\n")
                if len(lines) > 20:
                    structs.append(f"[Class]\n" + "\n".join(lines[:15]) + f"\n  ... ({len(lines)} lines)")
                else:
                    structs.append(f"[Class]\n{text}")
        return structs

    def _extract_top_comments(self, root, source: str) -> str:
        """Extract top-level comments (file-level documentation)."""
        comments: list[str] = []
        for node in root.children:
            if node.type == "comment":
                comments.append(source[node.start_byte:node.end_byte].strip())
            elif node.type not in ("preproc_include", "import_statement", "\n"):
                break  # Stop after first non-comment, non-import
        return "\n".join(comments)

    def _find_nodes(self, node, node_type: str) -> list:
        """Recursively find all nodes of a given type in the syntax tree."""
        results = []
        if node.type == node_type:
            results.append(node)
        for child in node.children:
            results.extend(self._find_nodes(child, node_type))
        return results
