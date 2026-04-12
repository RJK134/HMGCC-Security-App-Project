# Security Research Assistant - Claude Code Guide

## Project Overview
Smart Personal Assistant for Security Researchers (HMGCC Co-Creation Challenge CH-2026-001).
Helps security researchers characterise complex industrial machinery by ingesting, indexing, and querying
technical documentation (datasheets, schematics, manuals, code, images) using local LLM-powered RAG.

**Key Constraint: Fully offline operation. No internet calls. No telemetry.**

## Tech Stack
- **Backend**: Python 3.11+, FastAPI, Uvicorn, Pydantic
- **LLM**: Ollama (Mistral/Llama 3 quantized models, local inference)
- **Embeddings**: all-MiniLM-L6-v2 or nomic-embed-text (via Ollama/sentence-transformers)
- **Vector DB**: ChromaDB (embedded, no server)
- **SQL DB**: SQLite (conversations, user profiles, document metadata)
- **Document Processing**: PyMuPDF, Tesseract OCR, tree-sitter, PIL/OpenCV
- **RAG Framework**: LlamaIndex
- **Frontend**: Tauri + React + TypeScript
- **Testing**: pytest, Vitest

## Project Structure
```
security-research-assistant/
  backend/          # FastAPI application and API routes
  core/             # Core library modules
    ingest/         # Document ingestion and parsing pipeline
    rag/            # RAG engine, hybrid search, query processing
    conversation/   # Conversation memory and context management
    validation/     # Confidence scoring, hallucination detection
    architecture/   # System architecture characterisation
    profile/        # User profiling and adaptation
    reports/        # Report generation and export
  frontend/src/     # Tauri + React desktop app
  data/             # Local data storage (vectordb, sqlite, models)
  tests/            # Test suites mirroring core/ structure
  docs/             # User guide and API reference
```

## Commands
- `uvicorn backend.main:app --reload` — run backend dev server
- `pytest` — run all tests
- `pytest tests/test_ingest/` — run ingestion tests only
- `cd frontend && npm run dev` — run frontend dev server
- `cd frontend && npm run build` — build frontend for production

## Conventions
- See CONVENTIONS.md for coding standards
- All config via YAML files or environment variables, never hardcoded paths
- Every LLM response must pass through the validation pipeline before display
- All source data stays local — enforce no network calls
- Use structured logging throughout (Python `logging` module)
