"""Global exception handler middleware for FastAPI."""

from fastapi import Request
from fastapi.responses import JSONResponse

from core.exceptions import (
    ConversationNotFoundError,
    LLMConnectionError,
    ProjectNotFoundError,
    SRAError,
    ValidationError,
)
from core.logging import get_logger

log = get_logger(__name__)

# Map specific exceptions to HTTP status codes
_STATUS_MAP: dict[type, int] = {
    ProjectNotFoundError: 404,
    ConversationNotFoundError: 404,
    ValidationError: 422,
    LLMConnectionError: 503,
}


async def sra_exception_handler(request: Request, exc: SRAError) -> JSONResponse:
    """Convert SRAError subclasses to structured JSON error responses.

    Args:
        request: The incoming request.
        exc: The raised SRAError.

    Returns:
        JSONResponse with appropriate status code and error details.
    """
    status_code = _STATUS_MAP.get(type(exc), 500)
    log.error(
        "request_error",
        error_type=type(exc).__name__,
        message=exc.message,
        details=exc.details,
        path=str(request.url),
    )
    return JSONResponse(
        status_code=status_code,
        content={
            "error": type(exc).__name__,
            "message": exc.message,
            "details": exc.details,
        },
    )
