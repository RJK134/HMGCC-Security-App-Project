"""API response envelope schemas."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response from the /health endpoint."""

    status: str
    ollama_connected: bool
    available_models: list[str]
    database_ok: bool
    vector_store_ok: bool
    document_count: int


class ErrorResponse(BaseModel):
    """Standard error response envelope."""

    error: str
    message: str
    details: dict = {}
