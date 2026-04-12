"""FastAPI application entry point.

Creates the app, registers middleware, and manages startup/shutdown lifecycle.
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.v1.router import api_v1_router
from backend.config import get_settings
from backend.dependencies import get_db, get_ollama_client, get_vector_store
from backend.middleware.error_handler import sra_exception_handler
from backend.middleware.logging import RequestLoggingMiddleware
from core.exceptions import SRAError
from core.logging import configure_logging, get_logger

log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager — startup and shutdown hooks.

    Args:
        app: The FastAPI application instance.
    """
    settings = get_settings()
    configure_logging(log_level=settings.log_level)

    log.info("application_starting", host=settings.host, port=settings.port)

    # Initialize database
    db = get_db()
    log.info("database_ready", path=str(settings.sqlite_file))

    # Initialize vector store
    get_vector_store()
    log.info("vector_store_ready", path=str(settings.chroma_dir))

    # Check Ollama (warn if not running, don't crash)
    ollama = get_ollama_client()
    if ollama.health_check():
        models = ollama.list_models()
        log.info("ollama_connected", models=models)
    else:
        log.warning(
            "ollama_not_available",
            url=settings.ollama_base_url,
            message="Ollama is not running. LLM features will be unavailable.",
        )

    yield

    # Shutdown
    db.close()
    log.info("application_shutdown")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI app instance.
    """
    app = FastAPI(
        title="Security Research Assistant",
        description="Offline-first smart personal assistant for security researchers.",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS — allow localhost origins for Tauri frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:1420", "http://localhost:3000", "http://127.0.0.1:1420"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request logging
    app.add_middleware(RequestLoggingMiddleware)

    # Global error handler for all SRAError subclasses
    app.add_exception_handler(SRAError, sra_exception_handler)  # type: ignore[arg-type]

    # Routes
    app.include_router(api_v1_router)

    return app


app = create_app()
