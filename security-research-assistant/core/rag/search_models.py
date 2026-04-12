"""Shared data models for the search and RAG pipeline."""

from pydantic import BaseModel


class SearchResult(BaseModel):
    """A single search result from vector or keyword search."""

    chunk_id: str
    content: str
    score: float
    metadata: dict = {}
