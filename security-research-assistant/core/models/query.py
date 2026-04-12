"""Query request and response data models."""

from uuid import UUID

from pydantic import BaseModel, Field

from core.models.conversation import Citation


class QueryRequest(BaseModel):
    """A user query submitted to the RAG engine."""

    question: str
    conversation_id: UUID | None = None
    project_id: UUID


class ConfidenceResult(BaseModel):
    """Confidence assessment for a generated response."""

    score: float = Field(ge=0, le=100, description="Confidence score 0-100")
    explanation: str
    flagged_claims: list[str] = Field(default_factory=list)
    alternative_interpretations: list[str] = Field(default_factory=list)


class QueryResponse(BaseModel):
    """Complete response to a user query, after validation."""

    answer: str
    citations: list[Citation] = Field(default_factory=list)
    confidence: ConfidenceResult
    sources_used: int = 0
    retrieval_scores: dict = Field(default_factory=dict)
    suggested_queries: list[str] = Field(default_factory=list)
