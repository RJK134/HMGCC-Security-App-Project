"""Custom exception hierarchy for Security Research Assistant."""


class SRAError(Exception):
    """Base exception for all SRA errors."""


class ConfigurationError(SRAError):
    """Raised when configuration is invalid or missing."""


class IngestionError(SRAError):
    """Raised when document ingestion fails."""


class ParsingError(IngestionError):
    """Raised when a document cannot be parsed."""


class EmbeddingError(SRAError):
    """Raised when embedding generation fails."""


class QueryError(SRAError):
    """Raised when a RAG query fails."""


class LLMError(SRAError):
    """Raised when the local LLM is unavailable or returns an error."""


class ValidationError(SRAError):
    """Raised when response validation fails."""


class ConversationError(SRAError):
    """Raised when conversation operations fail."""


class DatabaseError(SRAError):
    """Raised when database operations fail."""


class ReportError(SRAError):
    """Raised when report generation fails."""
