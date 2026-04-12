"""Image parser with OCR using Pillow and Tesseract."""

from pathlib import Path

from core.ingest.parsers.base import BaseParser, ExtractedImage, ParseResult
from core.logging import get_logger

log = get_logger(__name__)


class ImageParser(BaseParser):
    """Extract text from images via OCR with pre-processing for quality."""

    def parse(self, filepath: Path) -> ParseResult:
        """Parse an image file, applying OCR to extract text.

        Pre-processes the image (grayscale, deskew, threshold) before OCR.
        Tries multiple Tesseract page segmentation modes and picks the best.

        Args:
            filepath: Path to the image file.

        Returns:
            ParseResult with OCR-extracted text and image metadata.
        """
        from PIL import Image, ImageFilter

        warnings: list[str] = []
        metadata: dict = {}

        try:
            img = Image.open(filepath)
        except Exception as e:
            warnings.append(f"Failed to open image: {e}")
            return ParseResult(text_content="", warnings=warnings)

        metadata = {
            "width": img.width,
            "height": img.height,
            "format": img.format or filepath.suffix.lstrip(".").upper(),
            "mode": img.mode,
        }

        # Try to get DPI
        dpi = img.info.get("dpi")
        if dpi:
            metadata["dpi"] = dpi

        # Pre-processing pipeline
        processed = self._preprocess(img)

        # Run OCR with multiple PSM modes, pick best
        text_psm6 = self._run_ocr(processed, psm=6)
        text_psm3 = self._run_ocr(processed, psm=3)

        # Pick the result with more extracted text
        ocr_text = text_psm6 if len(text_psm6) >= len(text_psm3) else text_psm3

        if not ocr_text.strip():
            warnings.append("OCR produced no text from this image.")

        # Store original image bytes
        import io
        buf = io.BytesIO()
        try:
            img.save(buf, format=img.format or "PNG")
        except Exception:
            img.save(buf, format="PNG")
        image_bytes = buf.getvalue()

        images = [ExtractedImage(
            image_bytes=image_bytes,
            ocr_text=ocr_text if ocr_text.strip() else None,
        )]

        log.info(
            "image_parsed",
            filepath=str(filepath),
            ocr_chars=len(ocr_text),
            dimensions=f"{img.width}x{img.height}",
        )
        return ParseResult(
            text_content=ocr_text,
            images=images,
            metadata=metadata,
            warnings=warnings,
        )

    def _preprocess(self, img: "Image.Image") -> "Image.Image":
        """Pre-process image for optimal OCR accuracy.

        Converts to grayscale, applies adaptive-like thresholding,
        and denoises with a median filter.
        """
        from PIL import Image, ImageFilter

        # Convert to grayscale
        if img.mode != "L":
            img = img.convert("L")

        # Denoise with median filter
        img = img.filter(ImageFilter.MedianFilter(size=3))

        # Simple binarisation via threshold (approximate adaptive)
        threshold = 128
        img = img.point(lambda p: 255 if p > threshold else 0, mode="1")
        img = img.convert("L")  # Back to grayscale for Tesseract

        return img

    def _run_ocr(self, img: "Image.Image", psm: int = 6) -> str:
        """Run Tesseract OCR with specified page segmentation mode.

        Args:
            img: Pre-processed PIL Image.
            psm: Tesseract page segmentation mode.

        Returns:
            Extracted text string, or empty string on failure.
        """
        try:
            import pytesseract
            config = f"--oem 3 --psm {psm}"
            return pytesseract.image_to_string(img, config=config).strip()
        except Exception as e:
            log.warning("ocr_failed", psm=psm, error=str(e))
            return ""
