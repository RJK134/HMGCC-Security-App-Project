"""Fixtures for RAG engine tests.

Provides a pre-populated ChromaDB and SQLite with test chunks to query against.
"""

from pathlib import Path
from uuid import UUID, uuid4

import pytest

from backend.config import Settings
from core.database.connection import DatabaseManager
from core.database.repositories.project_repo import ProjectRepository
from core.rag.search_models import SearchResult
from core.vector_store.chroma_client import ChromaVectorStore

# Consistent test UUIDs
TEST_PROJECT_ID = uuid4()
TEST_DOC_ID_1 = uuid4()
TEST_DOC_ID_2 = uuid4()

# Sample chunks about a microcontroller
SAMPLE_CHUNKS = [
    {
        "id": f"{TEST_DOC_ID_1}_0",
        "content": "The STM32F407VGT6 microcontroller is based on the ARM Cortex-M4 core "
                   "running at up to 168 MHz. It features 1 MB Flash memory and 192 KB SRAM.",
        "metadata": {
            "document_id": str(TEST_DOC_ID_1),
            "filename": "STM32F407_datasheet.pdf",
            "page_number": 1,
            "section_heading": "Overview",
            "source_tier": "tier_1_manufacturer",
            "document_type": "pdf",
        },
    },
    {
        "id": f"{TEST_DOC_ID_1}_1",
        "content": "GPIO Port A pins PA0-PA15 provide general purpose I/O. "
                   "SPI1 uses PA5 (SCK), PA6 (MISO), PA7 (MOSI). "
                   "I2C1 uses PB6 (SCL), PB7 (SDA). UART2 uses PA2 (TX), PA3 (RX).",
        "metadata": {
            "document_id": str(TEST_DOC_ID_1),
            "filename": "STM32F407_datasheet.pdf",
            "page_number": 2,
            "section_heading": "Pin Configuration",
            "source_tier": "tier_1_manufacturer",
            "document_type": "pdf",
        },
    },
    {
        "id": f"{TEST_DOC_ID_1}_2",
        "content": "Supply voltage VDD ranges from 1.8V to 3.6V. "
                   "Maximum current consumption is 150mA at 168MHz. "
                   "Operating temperature range is -40C to +85C industrial grade.",
        "metadata": {
            "document_id": str(TEST_DOC_ID_1),
            "filename": "STM32F407_datasheet.pdf",
            "page_number": 3,
            "section_heading": "Power Supply",
            "source_tier": "tier_1_manufacturer",
            "document_type": "pdf",
        },
    },
    {
        "id": f"{TEST_DOC_ID_2}_0",
        "content": "The Modbus RTU protocol is commonly used in industrial control systems. "
                   "It communicates over RS-485 serial interfaces. "
                   "The protocol has no built-in authentication mechanism.",
        "metadata": {
            "document_id": str(TEST_DOC_ID_2),
            "filename": "ICS_Security_Analysis.txt",
            "page_number": 1,
            "section_heading": "Protocols",
            "source_tier": "tier_3_trusted_forum",
            "document_type": "text",
        },
    },
    {
        "id": f"{TEST_DOC_ID_2}_1",
        "content": "The HMI web interface uses default credentials admin/admin. "
                   "Firmware update mechanism does not verify digital signatures. "
                   "These represent significant security vulnerabilities.",
        "metadata": {
            "document_id": str(TEST_DOC_ID_2),
            "filename": "ICS_Security_Analysis.txt",
            "page_number": 1,
            "section_heading": "Vulnerabilities",
            "source_tier": "tier_3_trusted_forum",
            "document_type": "text",
        },
    },
]


@pytest.fixture
def rag_db(tmp_path: Path) -> tuple[DatabaseManager, UUID]:
    """Database with project and chunk records for RAG tests."""
    db = DatabaseManager(tmp_path / "rag_test.db")
    db.initialize()
    conn = db.get_connection()

    # Create project
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO projects (id, name, created_at, updated_at) VALUES (?, ?, ?, ?)",
        (str(TEST_PROJECT_ID), "Test ICS Project", now, now),
    )

    # Create documents
    for doc_id, fname, ftype, tier in [
        (TEST_DOC_ID_1, "STM32F407_datasheet.pdf", "pdf", "tier_1_manufacturer"),
        (TEST_DOC_ID_2, "ICS_Security_Analysis.txt", "text", "tier_3_trusted_forum"),
    ]:
        conn.execute(
            "INSERT INTO documents (id, project_id, filename, filepath, filetype, "
            "size_bytes, status, source_tier, import_timestamp) "
            "VALUES (?, ?, ?, ?, ?, ?, 'indexed', ?, ?)",
            (str(doc_id), str(TEST_PROJECT_ID), fname, f"/data/{fname}", ftype, 1000, tier, now),
        )

    # Create chunks
    for chunk in SAMPLE_CHUNKS:
        conn.execute(
            "INSERT INTO chunks (id, document_id, content, chunk_index, "
            "page_number, section_heading, token_count, chroma_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                chunk["id"], chunk["metadata"]["document_id"], chunk["content"],
                int(chunk["id"].split("_")[-1]),
                chunk["metadata"]["page_number"],
                chunk["metadata"]["section_heading"],
                len(chunk["content"].split()),
                chunk["id"],
            ),
        )
    conn.commit()
    return db, TEST_PROJECT_ID


@pytest.fixture
def rag_chroma(tmp_path: Path) -> ChromaVectorStore:
    """ChromaDB with test chunk vectors for RAG tests."""
    chroma_dir = tmp_path / "rag_chroma"
    chroma_dir.mkdir()
    vs = ChromaVectorStore(chroma_dir)

    # Add chunks with simple deterministic embeddings
    vs.add_chunks(
        project_id=TEST_PROJECT_ID,
        ids=[c["id"] for c in SAMPLE_CHUNKS],
        embeddings=[[float(i) / 10 + 0.1 * j for j in range(384)] for i in range(len(SAMPLE_CHUNKS))],
        documents=[c["content"] for c in SAMPLE_CHUNKS],
        metadatas=[c["metadata"] for c in SAMPLE_CHUNKS],
    )
    return vs


@pytest.fixture
def sample_search_results() -> list[SearchResult]:
    """Pre-built SearchResult list for testing parsers and builders."""
    return [
        SearchResult(
            chunk_id=c["id"],
            content=c["content"],
            score=1.0 - i * 0.1,
            metadata=c["metadata"],
        )
        for i, c in enumerate(SAMPLE_CHUNKS)
    ]
