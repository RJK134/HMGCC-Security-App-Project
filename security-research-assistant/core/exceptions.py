"""Custom exception hierarchy for Security Research Assistant.

All application-specific exceptions inherit from SRAError.
Each carries an optional details dict for structured error context.
"""


class SRAError(Exception):
    """Base exception for all SRA errors."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConfigurationError(SRAError):
    """Raised when configuration is invalid or missing."""


class DocumentProcessingError(SRAError):
    """Raised when document ingestion or parsing fails."""


class EmbeddingError(SRAError):
    """Raised when embedding generation fails."""


class LLMConnectionError(SRAError):
    """Raised when Ollama is unreachable or a model is unavailable."""


class LLMInferenceError(SRAError):
    """Raised when the LLM returns an error during generation."""


class VectorStoreError(SRAError):
    """Raised when ChromaDB operations fail."""


class ConversationNotFoundError(SRAError):
    """Raised when a requested conversation does not exist."""


class ProjectNotFoundError(SRAError):
    """Raised when a requested project does not exist."""


class ValidationError(SRAError):
    """Raised when response validation fails."""


class DatabaseError(SRAError):
    """Raised when SQLite database operations fail."""
