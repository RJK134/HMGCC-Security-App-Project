"""Document ingestion pipeline orchestrator.

Coordinates file detection, parsing, chunking, embedding, and storage.
"""

import json
import traceback
from pathlib import Path
from uuid import UUID

from backend.config import Settings
from core.database.connection import DatabaseManager
from core.database.repositories.document_repo import DocumentRepository
from core.exceptions import DocumentProcessingError
from core.ingest.chunker import SemanticChunker
from core.ingest.detector import detect_file_type
from core.ingest.embedder import Embedder
from core.ingest.parsers.base import BaseParser, ExtractedImage, PageContent, ParseResult
from core.ingest.translator import Translator
from core.logging import get_logger
from core.models.document import DocumentMetadata, DocumentStatus, DocumentType, SourceTier
from core.vector_store.chroma_client import ChromaVectorStore

log = get_logger(__name__)

# Supported extensions for directory scanning
_SUPPORTED_EXTENSIONS = {
    ".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp",
    ".c", ".h", ".cpp", ".cc", ".hpp", ".py", ".asm", ".s",
    ".rs", ".go", ".java", ".sh", ".js", ".ts",
    ".txt", ".md", ".html", ".htm", ".xml", ".json", ".yaml", ".yml",
    ".csv", ".xlsx", ".xls", ".tsv",
}


class IngestionPipeline:
    """Orchestrate the full document ingestion workflow.

    Args:
        db: Database manager for SQLite operations.
        vector_store: ChromaDB wrapper for vector storage.
        embedder: Embedding generator.
        settings: Application settings.
    """

    def __init__(
        self,
        db: DatabaseManager,
        vector_store: ChromaVectorStore,
        embedder: Embedder,
        settings: Settings,
        translator: Translator | None = None,
    ) -> None:
        self._db = db
        self._vector_store = vector_store
        self._embedder = embedder
        self._settings = settings
        self._translator = translator
        self._doc_repo = DocumentRepository()
        self._chunker = SemanticChunker(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )
        self._parsers: dict[DocumentType, BaseParser] = self._build_parsers()

    @staticmethod
    def _build_parsers() -> dict[DocumentType, BaseParser]:
        """Build parser dict with lazy imports to avoid html.entities issues."""
        from core.ingest.parsers.code_parser import CodeParser
        from core.ingest.parsers.image_parser import ImageParser
        from core.ingest.parsers.spreadsheet_parser import SpreadsheetParser
        from core.ingest.parsers.text_parser import TextParser

        parsers: dict[DocumentType, BaseParser] = {
            DocumentType.IMAGE: ImageParser(),
            DocumentType.CODE: CodeParser(),
            DocumentType.TEXT: TextParser(),
            DocumentType.SPREADSHEET: SpreadsheetParser(),
        }

        # PDF parser depends on PyMuPDF which may fail on some Python versions
        try:
            from core.ingest.parsers.pdf_parser import PdfParser
            parsers[DocumentType.PDF] = PdfParser()
            parsers[DocumentType.SCHEMATIC] = PdfParser()
        except (ImportError, ModuleNotFoundError):
            log.warning("pdf_parser_unavailable", reason="PyMuPDF import failed")

        return parsers

    def ingest_file(
        self,
        filepath: Path,
        project_id: UUID,
        source_tier: SourceTier = SourceTier.TIER_4_UNVERIFIED,
    ) -> DocumentMetadata:
        """Ingest a single file through the full pipeline.

        Workflow: validate → detect type → create record → parse → chunk →
        embed → store vectors → store chunks → update status.

        Args:
            filepath: Path to the file to ingest.
            project_id: UUID of the target project.
            source_tier: Quality tier classification for this document.

        Returns:
            DocumentMetadata with final status (INDEXED or FAILED).
        """
        conn = self._db.get_connection()

        # Validate file
        if not filepath.exists():
            raise DocumentProcessingError(f"File not found: {filepath}")
        if not filepath.is_file():
            raise DocumentProcessingError(f"Not a file: {filepath}")

        # Detect type
        try:
            doc_type = detect_file_type(filepath)
        except DocumentProcessingError:
            raise
        except Exception as e:
            raise DocumentProcessingError(f"Type detection failed: {e}") from e

        # Create document record (PENDING)
        doc = self._doc_repo.create(
            conn,
            project_id=project_id,
            filename=filepath.name,
            filepath=filepath,
            filetype=doc_type,
            size_bytes=filepath.stat().st_size,
            source_tier=source_tier,
        )

        try:
            # Update to PROCESSING
            self._doc_repo.update_status(conn, doc.id, DocumentStatus.PROCESSING)

            # Parse
            parser = self._parsers.get(doc_type)
            if parser is None:
                raise DocumentProcessingError(f"No parser for type: {doc_type}")

            log.info("parsing_document", document_id=str(doc.id), type=doc_type.value)
            parse_result = parser.parse(filepath)
            parse_result = self._translate_if_needed(parse_result)

            if not parse_result.text_content.strip() and not parse_result.images:
                log.warning("empty_parse_result", document_id=str(doc.id))

            # Update page count from metadata
            page_count = parse_result.metadata.get("page_count")
            if page_count:
                conn.execute(
                    "UPDATE documents SET page_count = ? WHERE id = ?",
                    (page_count, str(doc.id)),
                )

            # Store parser/translation metadata and warnings
            if parse_result.metadata or parse_result.warnings:
                meta = json.loads(
                    conn.execute(
                        "SELECT metadata_json FROM documents WHERE id = ?", (str(doc.id),)
                    ).fetchone()[0] or "{}"
                )
                meta.update(parse_result.metadata)
                meta["parser_warnings"] = parse_result.warnings
                conn.execute(
                    "UPDATE documents SET metadata_json = ? WHERE id = ?",
                    (json.dumps(meta), str(doc.id)),
                )
                conn.commit()

            # Chunk
            log.info("chunking_document", document_id=str(doc.id))
            chunks = self._chunker.chunk_document(parse_result, doc.id)

            if not chunks:
                log.warning("no_chunks_produced", document_id=str(doc.id))
                self._doc_repo.update_status(conn, doc.id, DocumentStatus.INDEXED)
                return self._doc_repo.get_by_id(conn, doc.id) or doc

            # Embed
            log.info("embedding_chunks", document_id=str(doc.id), count=len(chunks))
            embeddings = self._embedder.embed_chunks(chunks)

            # Store in ChromaDB
            log.info("storing_vectors", document_id=str(doc.id), count=len(chunks))
            self._vector_store.add_chunks(
                project_id=project_id,
                ids=[c.chroma_id for c in chunks],
                embeddings=embeddings,
                documents=[c.content for c in chunks],
                metadatas=[
                    {
                        "document_id": str(c.document_id),
                        "filename": filepath.name,
                        "chunk_index": c.chunk_index,
                        "page_number": c.page_number or 0,
                        "section_heading": c.section_heading or "",
                        "document_type": doc_type.value,
                        "source_tier": source_tier.value,
                    }
                    for c in chunks
                ],
            )

            # Store chunk records in SQLite
            for chunk in chunks:
                conn.execute(
                    "INSERT INTO chunks (id, document_id, content, chunk_index, "
                    "page_number, section_heading, token_count, chroma_id) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        str(chunk.id), str(chunk.document_id), chunk.content,
                        chunk.chunk_index, chunk.page_number, chunk.section_heading,
                        chunk.token_count, chunk.chroma_id,
                    ),
                )
            conn.commit()

            # Update status to INDEXED
            self._doc_repo.update_status(conn, doc.id, DocumentStatus.INDEXED)
            log.info(
                "document_indexed",
                document_id=str(doc.id),
                chunks=len(chunks),
                filename=filepath.name,
            )

        except Exception as e:
            log.error(
                "ingestion_failed",
                document_id=str(doc.id),
                error=str(e),
                traceback=traceback.format_exc(),
            )
            # Update status to FAILED with error details
            meta = json.loads(
                conn.execute(
                    "SELECT metadata_json FROM documents WHERE id = ?", (str(doc.id),)
                ).fetchone()[0] or "{}"
            )
            meta["error"] = str(e)
            conn.execute(
                "UPDATE documents SET metadata_json = ?, status = ? WHERE id = ?",
                (json.dumps(meta), DocumentStatus.FAILED.value, str(doc.id)),
            )
            conn.commit()

        return self._doc_repo.get_by_id(conn, doc.id) or doc

    def _translate_if_needed(self, parse_result: ParseResult) -> ParseResult:
        """Translate non-English content for indexing while preserving originals.

        When translation is unavailable or low confidence, the original text is still
        indexed, but the generated bilingual wrapper explicitly marks that no usable
        English translation was produced.
        """
        if self._translator is None or not parse_result.text_content.strip():
            return parse_result

        sample = parse_result.text_content[:1000]
        if self._translator.is_english(sample):
            metadata = dict(parse_result.metadata)
            metadata.setdefault("original_language", "English")
            metadata.setdefault("translation_applied", False)
            return parse_result.model_copy(update={"metadata": metadata})

        source_language = self._translator.detect_language(sample)
        if source_language.lower() in {"unknown", "english"}:
            metadata = dict(parse_result.metadata)
            metadata.setdefault("original_language", source_language)
            metadata.setdefault("translation_applied", False)
            return parse_result.model_copy(update={"metadata": metadata})

        warnings = list(parse_result.warnings)
        metadata = dict(parse_result.metadata)
        metadata["original_language"] = source_language
        metadata["translation_applied"] = True

        translated_pages = [
            self._translate_page(page, source_language)
            for page in parse_result.pages
        ]
        translated_images = [
            self._translate_image(image, source_language)
            for image in parse_result.images
        ]

        if translated_pages:
            text_content = "\n\n".join(page.text for page in translated_pages if page.text.strip())
        else:
            translated_text, confidence = self._safe_translate_to_english(
                parse_result.text_content,
                source_language,
            )
            metadata["translation_confidence"] = confidence
            text_content = self._compose_bilingual_text(
                parse_result.text_content,
                translated_text,
                source_language,
                translation_available=confidence > 0.0,
            )
            if confidence == 0.0:
                warnings.append(
                    f"Translation to English failed for {source_language}; indexed original text only.",
                )

        return parse_result.model_copy(update={
            "text_content": text_content,
            "pages": translated_pages,
            "images": translated_images,
            "metadata": metadata,
            "warnings": warnings,
        })

    def _translate_page(self, page: PageContent, source_language: str) -> PageContent:
        """Translate a page while preserving the original text for provenance."""
        if not page.text.strip():
            return page

        translated_text, confidence = self._safe_translate_to_english(page.text, source_language)
        return page.model_copy(update={
            "text": self._compose_bilingual_text(
                page.text,
                translated_text,
                source_language,
                translation_available=confidence > 0.0,
            ),
        })

    def _translate_image(self, image: ExtractedImage, source_language: str) -> ExtractedImage:
        """Translate OCR text while keeping the original OCR content."""
        if not image.ocr_text or not image.ocr_text.strip():
            return image

        translated_text, confidence = self._safe_translate_to_english(
            image.ocr_text,
            source_language,
        )
        return image.model_copy(update={
            "ocr_text": self._compose_bilingual_text(
                image.ocr_text,
                translated_text,
                source_language,
                translation_available=confidence > 0.0,
            ),
        })

    def _safe_translate_to_english(
        self,
        text: str,
        source_language: str,
    ) -> tuple[str, float]:
        """Translate text without letting translator failures abort ingestion."""
        try:
            translation = self._translator.translate_to_english(text, source_language)
            return translation.translated_text.strip(), translation.confidence
        except Exception as exc:
            log.warning(
                "translation_failed_during_ingest",
                source_language=source_language,
                error=str(exc),
            )
            return "", 0.0

    @staticmethod
    def _compose_bilingual_text(
        original_text: str,
        translated_text: str,
        source_language: str,
        translation_available: bool = True,
    ) -> str:
        """Build indexable bilingual text preserving original and English translation."""
        translated = translated_text.strip()
        translation_header = "[English translation]"
        if not translation_available:
            translation_header = "[English translation unavailable — indexing original text]"
            translated = "No usable English translation was produced; review the original text above."
        elif not translated:
            translation_header = "[English translation unavailable — empty translation output]"
            translated = "The translator returned no English text; review the original text above."
        original = original_text.strip()
        return (
            f"[Original language: {source_language}]\n"
            f"[Original text]\n{original}\n\n"
            f"{translation_header}\n{translated}"
        )

    def ingest_directory(
        self,
        dir_path: Path,
        project_id: UUID,
        recursive: bool = True,
        source_tier: SourceTier = SourceTier.TIER_4_UNVERIFIED,
    ) -> list[DocumentMetadata]:
        """Ingest all supported files from a directory.

        Args:
            dir_path: Path to the directory.
            project_id: Target project UUID.
            recursive: Whether to scan subdirectories.
            source_tier: Default source tier for all files.

        Returns:
            List of DocumentMetadata for all processed files.
        """
        if not dir_path.is_dir():
            raise DocumentProcessingError(f"Not a directory: {dir_path}")

        # Collect supported files
        if recursive:
            files = [f for f in dir_path.rglob("*") if f.is_file() and f.suffix.lower() in _SUPPORTED_EXTENSIONS]
        else:
            files = [f for f in dir_path.iterdir() if f.is_file() and f.suffix.lower() in _SUPPORTED_EXTENSIONS]

        log.info("batch_import_starting", directory=str(dir_path), file_count=len(files))

        results: list[DocumentMetadata] = []
        succeeded = 0
        failed = 0

        for filepath in sorted(files):
            try:
                doc = self.ingest_file(filepath, project_id, source_tier)
                results.append(doc)
                if doc.status == DocumentStatus.INDEXED:
                    succeeded += 1
                else:
                    failed += 1
            except Exception as e:
                log.error("batch_file_failed", filepath=str(filepath), error=str(e))
                failed += 1

        log.info(
            "batch_import_complete",
            total=len(files),
            succeeded=succeeded,
            failed=failed,
        )
        return results
