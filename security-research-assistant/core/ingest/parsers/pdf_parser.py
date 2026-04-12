"""PDF parser using PyMuPDF (fitz) for text, image, and table extraction."""

from pathlib import Path

from core.ingest.parsers.base import BaseParser, ExtractedImage, PageContent, ParseResult
from core.logging import get_logger

log = get_logger(__name__)

_MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB


class PdfParser(BaseParser):
    """Extract text, images, and tables from PDF documents using PyMuPDF."""

    def parse(self, filepath: Path) -> ParseResult:
        """Parse a PDF file extracting text, images, and tables per page.

        Args:
            filepath: Path to the PDF file.

        Returns:
            ParseResult with page-level text, extracted images, and metadata.
        """
        import fitz  # PyMuPDF

        warnings: list[str] = []
        pages: list[PageContent] = []
        images: list[ExtractedImage] = []
        metadata: dict = {}

        # Size check
        file_size = filepath.stat().st_size
        if file_size > _MAX_FILE_SIZE:
            warnings.append(f"File exceeds 500MB limit ({file_size} bytes), skipping.")
            return ParseResult(
                text_content="", metadata={"file_size": file_size}, warnings=warnings,
            )

        try:
            doc = fitz.open(str(filepath))
        except fitz.FileDataError as e:
            warnings.append(f"Corrupted or encrypted PDF: {e}")
            return ParseResult(text_content="", warnings=warnings)
        except Exception as e:
            warnings.append(f"Failed to open PDF: {e}")
            return ParseResult(text_content="", warnings=warnings)

        try:
            # Capture PDF metadata
            pdf_meta = doc.metadata or {}
            metadata = {
                "page_count": doc.page_count,
                "title": pdf_meta.get("title", ""),
                "author": pdf_meta.get("author", ""),
                "creation_date": pdf_meta.get("creationDate", ""),
                "file_size": file_size,
            }

            for page_num in range(doc.page_count):
                try:
                    page = doc[page_num]
                    page_text = self._extract_page_text(page)
                    page_tables = self._extract_tables(page)
                    page_images = self._extract_images(page, page_num + 1)

                    pages.append(PageContent(
                        page_number=page_num + 1,
                        text=page_text,
                        tables=page_tables,
                    ))
                    images.extend(page_images)

                except Exception as e:
                    warnings.append(f"Error processing page {page_num + 1}: {e}")
                    pages.append(PageContent(page_number=page_num + 1, text=""))

        finally:
            doc.close()

        full_text = "\n\n".join(p.text for p in pages if p.text.strip())

        log.info(
            "pdf_parsed",
            filepath=str(filepath),
            pages=len(pages),
            images=len(images),
            text_length=len(full_text),
        )
        return ParseResult(
            text_content=full_text, pages=pages, images=images,
            metadata=metadata, warnings=warnings,
        )

    def _extract_page_text(self, page) -> str:  # type: ignore[no-untyped-def]
        """Extract text from a page handling multi-column layouts.

        Uses block-level extraction sorted by position for reading order.
        """
        blocks = page.get_text("blocks")
        if not blocks:
            return page.get_text("text")

        # Sort by vertical then horizontal position for reading order
        # blocks: (x0, y0, x1, y1, text, block_no, block_type)
        text_blocks = [b for b in blocks if b[6] == 0]  # type 0 = text
        text_blocks.sort(key=lambda b: (round(b[1] / 20) * 20, b[0]))

        return "\n".join(b[4].strip() for b in text_blocks if b[4].strip())

    def _extract_tables(self, page) -> list[dict]:  # type: ignore[no-untyped-def]
        """Extract tables from a page using PyMuPDF's table finder."""
        tables: list[dict] = []
        try:
            found = page.find_tables()
            for i, table in enumerate(found.tables):
                rows = table.extract()
                if rows:
                    tables.append({
                        "table_index": i,
                        "headers": rows[0] if rows else [],
                        "rows": rows[1:] if len(rows) > 1 else [],
                    })
        except Exception:
            pass  # Table extraction is best-effort
        return tables

    def _extract_images(self, page, page_number: int) -> list[ExtractedImage]:  # type: ignore[no-untyped-def]
        """Extract images from a page, running OCR on large images."""
        extracted: list[ExtractedImage] = []
        try:
            image_list = page.get_images(full=True)
            doc = page.parent
            for img_ref in image_list:
                try:
                    xref = img_ref[0]
                    pix = doc.extract_image(xref)
                    if pix and pix.get("image"):
                        img_bytes = pix["image"]
                        # Only process substantial images (>5KB likely contain content)
                        ocr_text = None
                        if len(img_bytes) > 5000:
                            ocr_text = self._ocr_image_bytes(img_bytes)

                        extracted.append(ExtractedImage(
                            image_bytes=img_bytes,
                            page_number=page_number,
                            ocr_text=ocr_text,
                        ))
                except Exception:
                    continue  # Skip individual broken images
        except Exception:
            pass
        return extracted

    def _ocr_image_bytes(self, image_bytes: bytes) -> str | None:
        """Attempt OCR on image bytes. Returns None if OCR unavailable."""
        try:
            import io

            from PIL import Image
            import pytesseract

            img = Image.open(io.BytesIO(image_bytes))
            text = pytesseract.image_to_string(img, config="--oem 3 --psm 6").strip()
            return text if text else None
        except Exception:
            return None
