"""Tests for ChromaDB vector store wrapper."""

from pathlib import Path
from uuid import uuid4

import pytest

from core.vector_store.chroma_client import ChromaVectorStore


@pytest.fixture
def vector_store(chroma_dir: Path) -> ChromaVectorStore:
    """Provide a ChromaVectorStore using a temp directory."""
    return ChromaVectorStore(persist_directory=chroma_dir)


class TestChromaVectorStore:
    """Tests for ChromaDB operations."""

    def test_heartbeat(self, vector_store: ChromaVectorStore) -> None:
        """heartbeat() should return True when ChromaDB is initialised."""
        assert vector_store.heartbeat() is True

    def test_get_or_create_collection(self, vector_store: ChromaVectorStore) -> None:
        """get_or_create_collection() should create and return a collection."""
        project_id = uuid4()
        collection = vector_store.get_or_create_collection(project_id)
        assert collection is not None
        assert collection.count() == 0

    def test_add_and_count(self, vector_store: ChromaVectorStore) -> None:
        """add_chunks() should store chunks, count() should reflect them."""
        project_id = uuid4()
        doc_id = uuid4()
        vector_store.add_chunks(
            project_id=project_id,
            ids=["chunk_1", "chunk_2", "chunk_3"],
            embeddings=[[0.1] * 10, [0.2] * 10, [0.3] * 10],
            documents=["First chunk", "Second chunk", "Third chunk"],
            metadatas=[
                {"document_id": str(doc_id), "chunk_index": 0},
                {"document_id": str(doc_id), "chunk_index": 1},
                {"document_id": str(doc_id), "chunk_index": 2},
            ],
        )
        assert vector_store.count(project_id) == 3

    def test_query(self, vector_store: ChromaVectorStore) -> None:
        """query() should return relevant results."""
        project_id = uuid4()
        vector_store.add_chunks(
            project_id=project_id,
            ids=["c1", "c2"],
            embeddings=[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
            documents=["About processors", "About memory"],
            metadatas=[{"topic": "cpu"}, {"topic": "ram"}],
        )
        results = vector_store.query(
            project_id=project_id,
            query_embedding=[1.0, 0.0, 0.0],
            n_results=1,
        )
        assert len(results["ids"][0]) == 1
        assert results["documents"][0][0] == "About processors"

    def test_delete_by_document(self, vector_store: ChromaVectorStore) -> None:
        """delete_by_document() should remove all chunks for a document."""
        project_id = uuid4()
        doc_id = uuid4()
        other_doc_id = uuid4()
        vector_store.add_chunks(
            project_id=project_id,
            ids=["d1_c1", "d1_c2", "d2_c1"],
            embeddings=[[0.1] * 5, [0.2] * 5, [0.3] * 5],
            documents=["Doc1 chunk1", "Doc1 chunk2", "Doc2 chunk1"],
            metadatas=[
                {"document_id": str(doc_id)},
                {"document_id": str(doc_id)},
                {"document_id": str(other_doc_id)},
            ],
        )
        assert vector_store.count(project_id) == 3
        vector_store.delete_by_document(project_id, doc_id)
        assert vector_store.count(project_id) == 1

    def test_delete_collection(self, vector_store: ChromaVectorStore) -> None:
        """delete_collection() should remove the entire collection."""
        project_id = uuid4()
        vector_store.add_chunks(
            project_id=project_id,
            ids=["x1"],
            embeddings=[[0.1] * 3],
            documents=["test"],
            metadatas=[{"k": "v"}],
        )
        vector_store.delete_collection(project_id)
        # After deletion, get_or_create returns a fresh empty collection
        assert vector_store.count(project_id) == 0
