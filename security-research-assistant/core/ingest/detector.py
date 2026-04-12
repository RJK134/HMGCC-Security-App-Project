"""File type detection by extension and magic bytes validation."""

from pathlib import Path

from core.exceptions import DocumentProcessingError
from core.logging import get_logger
from core.models.document import DocumentType

log = get_logger(__name__)

# Extension to DocumentType mapping
_EXTENSION_MAP: dict[str, DocumentType] = {
    ".pdf": DocumentType.PDF,
    # Images
    ".png": DocumentType.IMAGE,
    ".jpg": DocumentType.IMAGE,
    ".jpeg": DocumentType.IMAGE,
    ".tiff": DocumentType.IMAGE,
    ".tif": DocumentType.IMAGE,
    ".bmp": DocumentType.IMAGE,
    # Code
    ".c": DocumentType.CODE,
    ".h": DocumentType.CODE,
    ".cpp": DocumentType.CODE,
    ".cc": DocumentType.CODE,
    ".hpp": DocumentType.CODE,
    ".py": DocumentType.CODE,
    ".asm": DocumentType.CODE,
    ".s": DocumentType.CODE,
    ".rs": DocumentType.CODE,
    ".go": DocumentType.CODE,
    ".java": DocumentType.CODE,
    ".sh": DocumentType.CODE,
    ".js": DocumentType.CODE,
    ".ts": DocumentType.CODE,
    # Text
    ".txt": DocumentType.TEXT,
    ".md": DocumentType.TEXT,
    ".html": DocumentType.TEXT,
    ".htm": DocumentType.TEXT,
    ".xml": DocumentType.TEXT,
    ".json": DocumentType.TEXT,
    ".yaml": DocumentType.TEXT,
    ".yml": DocumentType.TEXT,
    ".rst": DocumentType.TEXT,
    ".log": DocumentType.TEXT,
    # Spreadsheets
    ".csv": DocumentType.SPREADSHEET,
    ".xlsx": DocumentType.SPREADSHEET,
    ".xls": DocumentType.SPREADSHEET,
    ".tsv": DocumentType.SPREADSHEET,
}

# Magic byte signatures for validation
_MAGIC_BYTES: dict[bytes, DocumentType] = {
    b"%PDF": DocumentType.PDF,
    b"\x89PNG": DocumentType.IMAGE,
    b"\xff\xd8\xff": DocumentType.IMAGE,  # JPEG
    b"BM": DocumentType.IMAGE,  # BMP
    b"II\x2a\x00": DocumentType.IMAGE,  # TIFF little-endian
    b"MM\x00\x2a": DocumentType.IMAGE,  # TIFF big-endian
    b"PK\x03\x04": DocumentType.SPREADSHEET,  # ZIP-based (xlsx)
}


def detect_file_type(filepath: Path) -> DocumentType:
    """Detect the document type of a file by extension, validated with magic bytes.

    Args:
        filepath: Path to the file.

    Returns:
        The detected DocumentType.

    Raises:
        DocumentProcessingError: If the file type is unsupported or the file
            cannot be read.
    """
    if not filepath.exists():
        raise DocumentProcessingError(
            f"File not found: {filepath}",
            details={"filepath": str(filepath)},
        )

    ext = filepath.suffix.lower()
    doc_type = _EXTENSION_MAP.get(ext)

    if doc_type is None:
        raise DocumentProcessingError(
            f"Unsupported file type: {ext}",
            details={"filepath": str(filepath), "extension": ext},
        )

    # Validate with magic bytes for binary formats
    try:
        with open(filepath, "rb") as f:
            header = f.read(8)
        for magic, magic_type in _MAGIC_BYTES.items():
            if header.startswith(magic):
                if doc_type != magic_type:
                    log.warning(
                        "file_type_mismatch",
                        filepath=str(filepath),
                        extension_type=doc_type.value,
                        magic_type=magic_type.value,
                    )
                    # Trust magic bytes over extension for binary formats
                    doc_type = magic_type
                break
    except OSError:
        # Can't read file for magic byte check, trust extension
        log.warning("magic_bytes_read_failed", filepath=str(filepath))

    log.info("file_type_detected", filepath=str(filepath), type=doc_type.value)
    return doc_type
