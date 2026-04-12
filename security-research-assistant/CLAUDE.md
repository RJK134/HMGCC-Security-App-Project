# CLAUDE.md — Project Intelligence for Claude Code

## Project Identity

**Name:** Security Research Assistant (SRA)
**Purpose:** Offline-first smart personal assistant for security researchers conducting hardware/software vulnerability assessments on industrial control systems.
**Client:** HMGCC Co-Creation (Challenge ID: CH-2026-001)
**Target:** Technology Readiness Level 6 — working prototype demonstrated in relevant environment
**Budget:** £60,000 | **Duration:** 12 weeks | **Kick-off:** July 2026

## Critical Constraint

> **THE TOOL MUST WORK ENTIRELY OFFLINE — NO INTERNET CONNECTION.**
> Every dependency, every model, every feature must function on an air-gapped laptop.
> Never introduce any code that makes network calls, fetches remote resources, or depends on cloud APIs.
> This is a national security tool used in classified environments.

## What This Tool Does

A security researcher receives a complex industrial machine (e.g., an additive manufacturing system used in defence). They must tear it down, understand every component, and identify vulnerabilities. Before expert analysis begins, they spend weeks collecting open-source technical information — datasheets, schematics, firmware code, forum posts, vendor manuals — about hundreds of micro-components.

This tool eliminates that bottleneck. The researcher imports all collected source material, and the tool:

1. **Indexes** structured and unstructured technical data about the product and its components
2. **Generates** clear technical summaries of the product and individual components
3. **Allows** natural-language conversational queries with cited, confidence-scored answers
4. **Remembers** conversation context across sessions spanning weeks
5. **Validates** all responses against source material to prevent hallucination
6. **Adapts** to the researcher's working style over time

## Technology Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Local LLM | Ollama | Runs Mistral 7B, Llama 3 8B, or similar quantised models locally |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) OR nomic-embed-text via Ollama | Must be local |
| Vector DB | ChromaDB | Embedded, no server process, Python-native |
| Backend | Python 3.11+ with FastAPI | Orchestration, RAG pipeline, API |
| Frontend | Tauri 2.x + React 18 + TypeScript | Desktop app with native feel |
| Document Processing | PyMuPDF, Tesseract OCR, Pillow, tree-sitter | Multi-modal parsing |
| Relational DB | SQLite | Conversations, user profiles, document metadata, source tracking |
| Search | Hybrid: ChromaDB vector search + rank-bm25 keyword search | Reciprocal Rank Fusion |

## Architecture Overview
```
[Tauri Desktop App (React/TypeScript)]
            │
            ▼
[FastAPI Backend (Python)]
    ├── Document Ingestion Pipeline
    │     ├── PDF Parser (PyMuPDF)
    │     ├── Image/OCR (Tesseract + Pillow)
    │     ├── Code Parser (tree-sitter)
    │     ├── Semantic Chunker
    │     └── Embedding Generator
    ├── RAG Query Engine
    │     ├── Hybrid Search (Vector + BM25)
    │     ├── Re-ranker
    │     ├── Context Assembler
    │     └── LLM Interface (Ollama)
    ├── Validation Engine
    │     ├── Confidence Scorer
    │     ├── Hallucination Detector
    │     └── Source Cross-Referrer
    ├── Conversation Manager
    │     ├── Session History (SQLite)
    │     ├── Context Reconstructor
    │     └── Long-term Memory (Pinned Facts)
    └── User Profile Engine
          ├── Preference Tracker
          └── Adaptive Prompting
            │
    ┌───────┼───────┐
    ▼       ▼       ▼
[ChromaDB] [SQLite] [Ollama]
```

## File Organization Conventions

- `/backend/` — FastAPI app, API routes, config, middleware
- `/backend/api/v1/` — Versioned API route modules (documents, query, conversations, reports, settings)
- `/core/` — All business logic, completely framework-agnostic (no FastAPI imports here)
- `/core/ingest/` — Document parsing, chunking, embedding pipeline
- `/core/rag/` — RAG engine: search, retrieval, context assembly, LLM interaction
- `/core/conversation/` — Conversation CRUD, memory, context reconstruction
- `/core/validation/` — Confidence scoring, hallucination detection, source verification
- `/core/architecture/` — System/component extraction, relationship mapping
- `/core/profile/` — User profiling, preference learning, adaptive behaviour
- `/core/reports/` — Report generation and export
- `/core/models/` — Pydantic data models shared across modules
- `/core/database/` — SQLite connection management, schema, migrations
- `/frontend/src/` — React + TypeScript source for Tauri app
- `/frontend/src/components/` — Reusable UI components
- `/frontend/src/pages/` — Page-level views (Chat, Library, Projects, Settings)
- `/frontend/src/hooks/` — Custom React hooks for API interaction
- `/frontend/src/stores/` — State management (Zustand)
- `/data/` — Runtime data directory (gitignored except structure)
- `/tests/` — Mirrors `/core/` structure. Every module has corresponding tests.
- `/docs/` — User and developer documentation

## Coding Standards

### Python (Backend + Core)
- Python 3.11+ with type hints on ALL function signatures
- Pydantic v2 for all data models and validation
- async/await for all I/O-bound operations in FastAPI
- Core library (`/core/`) must be synchronous and framework-agnostic — no FastAPI dependencies
- Use `pathlib.Path` not `os.path` for all file operations
- Logging via `structlog` with structured JSON output
- Docstrings on all public functions (Google style)
- Max line length: 100 characters
- Import ordering: stdlib → third-party → local (enforced by ruff)

### TypeScript (Frontend)
- Strict TypeScript (`strict: true` in tsconfig)
- Functional components with hooks only (no class components)
- Zustand for state management
- TanStack Query for API data fetching
- Tailwind CSS for styling
- Component files: PascalCase (e.g., `ChatMessage.tsx`)
- Hook files: camelCase with `use` prefix (e.g., `useConversation.ts`)

### Testing
- pytest for all Python tests
- Test file naming: `test_<module>.py`
- Minimum test coverage target: 80%
- Every public function in `/core/` must have at least one test
- Use pytest fixtures for database and file system setup
- Integration tests in `/tests/integration/`
- Frontend tests: Vitest + React Testing Library

### Error Handling
- Custom exception hierarchy rooted at `SRAError` in `/core/exceptions.py`
- Never catch bare `Exception` — always specific types
- All user-facing errors must have human-readable messages
- Log full stack traces at ERROR level, user-facing messages at WARNING

### Configuration
- All configuration via `/backend/config.py` using pydantic-settings
- Environment variables with `SRA_` prefix (e.g., `SRA_OLLAMA_MODEL`)
- Sensible defaults for all settings — tool must work out of the box
- Configuration file: `config.yaml` in project root (optional override)

## Key Design Decisions

1. **Core library is framework-agnostic.** The `/core/` package has zero knowledge of FastAPI, Tauri, or any HTTP framework. It exposes Python classes and functions. The FastAPI layer in `/backend/` is a thin wrapper. This means the core can be tested independently, reused in CLI tools, or wrapped in a different framework.

2. **Hybrid search is mandatory, not optional.** Security researchers search for exact part numbers (BM25 wins) AND conceptual questions about how systems work (vector search wins). Both must be present from day one, merged via Reciprocal Rank Fusion.

3. **Every LLM response goes through validation.** No raw LLM output ever reaches the user. The validation pipeline checks for hallucination, assigns confidence, and maps citations. This is non-negotiable for a security research tool.

4. **Conversation memory uses summarisation, not full history.** LLM context windows are limited on local models. Old messages are summarised. Key findings are stored as pinned facts. Context is reconstructed on session resume.

5. **Source provenance is a first-class citizen.** Every chunk in ChromaDB carries full metadata: source file path, page number, document type, import timestamp, user-assigned quality tier. Every answer citation maps back to this metadata.

## Build Order (Phase by Phase)

Follow this exact sequence. Each phase builds on the previous. Do not skip ahead.

### Phase 1: Foundation (Complete first — nothing else works without this)
1. Project scaffolding: pyproject.toml, directory structure, configuration
2. SQLite database: schema, connection management, migrations
3. Ollama integration: model detection, health check, basic inference
4. ChromaDB: collection creation, basic CRUD
5. FastAPI skeleton: health endpoint, CORS, error handling middleware
6. **VERIFY:** `pytest tests/` passes. Server starts. Ollama responds. ChromaDB stores and retrieves.

### Phase 2: Document Ingestion
1. File type detection and routing
2. PDF parser (PyMuPDF) with text + image extraction
3. Image/OCR parser (Tesseract)
4. Code parser (tree-sitter for C, Python, assembly)
5. Semantic chunking with metadata preservation
6. Embedding generation (local model)
7. ChromaDB storage with full metadata
8. SQLite document tracking (status, errors, metadata)
9. Batch import (directory scan)
10. API endpoints: upload, status, list documents
11. **VERIFY:** Import a PDF, image, and code file. Query ChromaDB — correct chunks with metadata. SQLite tracks all documents.

### Phase 3: RAG Query Engine
1. Vector similarity search (ChromaDB)
2. BM25 keyword search (rank_bm25 library)
3. Reciprocal Rank Fusion merger
4. Context assembly with token-aware truncation
5. LLM prompt construction with system instructions for citation
6. Response parsing: extract claims, map to sources
7. API endpoint: POST /api/v1/query
8. **VERIFY:** 20 test queries against ingested data. Answers are relevant, cited, and grounded.

### Phase 4: Validation & Confidence
1. Source quality tier classification (4 tiers)
2. Confidence scoring algorithm
3. Hallucination detection (claim vs evidence comparison)
4. Cross-reference engine
5. Validation pipeline integration (wraps all LLM responses)
6. **VERIFY:** Adversarial test queries. Confidence scores correlate with source quality. Hallucinations flagged.

### Phase 5: Conversation Management
1. Conversation CRUD (SQLite)
2. Message storage with timestamps
3. Conversation summary generation (LLM-assisted)
4. Context reconstruction on session resume
5. Pinned facts system
6. Multi-thread conversation support
7. API endpoints: conversations CRUD
8. **VERIFY:** Create conversation, send 10 messages, close, reopen — context reconstructed correctly.

### Phase 6: Desktop UI
1. Tauri + React project setup
2. Application shell: sidebar, routing, layout
3. Chat interface: message bubbles, markdown, citations, confidence badges
4. Data import: drag-and-drop zone, library grid/list view
5. Project management: create/switch projects
6. Settings panel: model selection, preferences
7. Source viewer panel: show cited documents
8. **VERIFY:** Full user workflow: create project → import documents → ask questions → receive cited answers.

### Phase 7: Advanced Features
1. System architecture extraction and component mapping
2. Report generation (PDF, Markdown export)
3. User profiling and adaptive behaviour
4. Non-English data support (translation pipeline)
5. **VERIFY:** Generate architecture diagram from test data. Export PDF report. Profile adapts after 20+ queries.

### Phase 8: Testing & Packaging
1. Full integration test suite
2. Performance benchmarks (response time, memory, disk)
3. Offline verification (zero network calls)
4. Tauri packaging: Windows NSIS installer, Linux AppImage
5. First-run wizard
6. Documentation
7. **VERIFY:** Install from package on clean machine. Full workflow works offline. All tests pass.

## Common Pitfalls to Avoid

- **Do NOT use OpenAI, Anthropic, or any cloud LLM API.** Everything goes through local Ollama.
- **Do NOT use `requests` or `httpx` to call external URLs.** The only HTTP calls are to localhost (Ollama, internal API).
- **Do NOT use LangChain's cloud-dependent features.** If using LangChain, only use local-compatible components. Prefer LlamaIndex or custom implementation.
- **Do NOT hardcode file paths.** Use configuration and `pathlib`.
- **Do NOT store embeddings as JSON files.** Use ChromaDB.
- **Do NOT ignore error handling on document parsing.** Corrupted files, weird encodings, and huge files are all expected. Handle gracefully.
- **Do NOT skip source attribution.** Every chunk, every answer, every report must trace back to its source file.

## Testing Commands
```bash
# Run all tests
pytest tests/ -v

# Run specific test module
pytest tests/test_ingest/ -v

# Run with coverage
pytest tests/ --cov=core --cov=backend --cov-report=html

# Run only unit tests (fast)
pytest tests/ -v -m "not integration"

# Run integration tests (requires Ollama running)
pytest tests/ -v -m integration

# Lint and format
ruff check .
ruff format .

# Type checking
mypy core/ backend/

# Frontend tests
cd frontend && npm test

# Frontend lint
cd frontend && npm run lint
```

## Running the Application
```bash
# Start Ollama (must be running before backend)
ollama serve

# Pull required model (first time only)
ollama pull mistral:7b-instruct-v0.3-q4_K_M

# Start backend
cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Start frontend (development)
cd frontend && npm run tauri dev

# Or start everything with the dev script
python scripts/dev.py
```

## Key Environment Variables
```
SRA_OLLAMA_BASE_URL=http://localhost:11434
SRA_OLLAMA_MODEL=mistral:7b-instruct-v0.3-q4_K_M
SRA_OLLAMA_EMBED_MODEL=nomic-embed-text
SRA_CHROMA_PATH=./data/vectordb
SRA_SQLITE_PATH=./data/sqlite/sra.db
SRA_LOG_LEVEL=INFO
SRA_CHUNK_SIZE=512
SRA_CHUNK_OVERLAP=50
SRA_TOP_K=10
SRA_MAX_CONTEXT_TOKENS=4096
```
