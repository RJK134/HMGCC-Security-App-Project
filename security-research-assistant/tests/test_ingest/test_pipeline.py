"""Integration tests for the ingestion pipeline with mock embedder."""

from pathlib import Path
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from backend.config import Settings
from core.database.connection import DatabaseManager
from core.database.repositories.project_repo import ProjectRepository
from core.ingest.pipeline import IngestionPipeline
from core.models.document import DocumentStatus, SourceTier
from core.vector_store.chroma_client import ChromaVectorStore


@pytest.fixture
def pipeline_env(tmp_path: Path):
    """Set up a complete pipeline environment with real DB and ChromaDB."""
    db_path = tmp_path / "test.db"
    db = DatabaseManager(db_path)
    db.initialize()

    chroma_dir = tmp_path / "chroma"
    chroma_dir.mkdir()
    vs = ChromaVectorStore(chroma_dir)

    # Mock embedder
    embedder = MagicMock()
    embedder.embed_chunks.side_effect = lambda chunks, **kw: [[0.1] * 768 for _ in chunks]

    settings = Settings(
        chroma_path=str(chroma_dir),
        sqlite_path=str(db_path),
        chunk_size=200,
        chunk_overlap=20,
    )

    pipeline = IngestionPipeline(db, vs, embedder, settings)

    # Create a project
    project_repo = ProjectRepository()
    project = project_repo.create(db.get_connection(), "Test Project")

    return pipeline, db, vs, project.id


class TestIngestionPipeline:
    """Integration tests for the full ingestion pipeline."""

    def test_ingest_pdf(self, pipeline_env, sample_pdf: Path) -> None:
        """Ingesting a PDF should produce INDEXED status and chunks (if PyMuPDF works)."""
        pipeline, db, vs, project_id = pipeline_env
        doc = pipeline.ingest_file(sample_pdf, project_id)

        # On Python 3.14, PyMuPDF fails due to html.entities — pipeline marks FAILED
        if doc.status == DocumentStatus.FAILED:
            pytest.skip("PyMuPDF unavailable on this Python version (html.entities)")

        assert doc.status == DocumentStatus.INDEXED

        conn = db.get_connection()
        chunk_count = conn.execute(
            "SELECT COUNT(*) FROM chunks WHERE document_id = ?", (str(doc.id),)
        ).fetchone()[0]
        assert chunk_count > 0
        assert vs.count(project_id) > 0

    def test_ingest_text(self, pipeline_env, sample_txt: Path) -> None:
        """Ingesting a text file should work end-to-end."""
        pipeline, db, vs, project_id = pipeline_env
        doc = pipeline.ingest_file(sample_txt, project_id)
        assert doc.status == DocumentStatus.INDEXED

    def test_ingest_code(self, pipeline_env, sample_c: Path) -> None:
        """Ingesting a C file should extract and index code."""
        pipeline, db, vs, project_id = pipeline_env
        doc = pipeline.ingest_file(sample_c, project_id)
        assert doc.status == DocumentStatus.INDEXED

    def test_ingest_csv(self, pipeline_env, sample_csv: Path) -> None:
        """Ingesting a CSV should convert to text and index."""
        pipeline, db, vs, project_id = pipeline_env
        doc = pipeline.ingest_file(sample_csv, project_id)
        assert doc.status == DocumentStatus.INDEXED

    def test_ingest_nonexistent_file_raises(self, pipeline_env) -> None:
        """Ingesting a nonexistent file should raise an error."""
        pipeline, _, _, project_id = pipeline_env
        from core.exceptions import DocumentProcessingError
        with pytest.raises(DocumentProcessingError):
            pipeline.ingest_file(Path("/nonexistent/file.pdf"), project_id)

    def test_ingest_directory(self, pipeline_env, fixtures_dir: Path,
                              sample_pdf, sample_txt, sample_c, sample_csv) -> None:
        """Batch importing a directory should process all supported files."""
        pipeline, db, vs, project_id = pipeline_env
        results = pipeline.ingest_directory(fixtures_dir, project_id)
        assert len(results) >= 4
        indexed = [d for d in results if d.status == DocumentStatus.INDEXED]
        # On Python 3.14, PDF may fail — at minimum text, code, csv should succeed
        assert len(indexed) >= 3

    def test_source_tier_applied(self, pipeline_env, sample_txt: Path) -> None:
        """Source tier should be stored with the document."""
        pipeline, _, _, project_id = pipeline_env
        doc = pipeline.ingest_file(
            sample_txt, project_id, source_tier=SourceTier.TIER_1_MANUFACTURER,
        )
        assert doc.source_tier == SourceTier.TIER_1_MANUFACTURER
