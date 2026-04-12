# ARCHITECTURE.md — System Architecture & Design Decisions

## System Overview

The Security Research Assistant (SRA) is a fully offline desktop application that enables
security researchers to import, index, search, and interrogate large collections of
technical documents about industrial control system products.

## Design Principles

1. **Offline-First:** No network dependency. Everything runs locally.
2. **Source-Grounded:** Every answer traces to source documents. No unverified claims.
3. **Framework-Agnostic Core:** Business logic in `/core/` has zero framework dependencies.
4. **Modular Pipeline:** Each processing stage is independent and testable.
5. **Graceful Degradation:** Bad inputs (corrupted files, ambiguous queries) produce helpful errors, not crashes.
6. **Security-Conscious:** No telemetry, no logging to external services, no data leakage.

## Component Architecture

### 1. Frontend Layer (Tauri + React)
```
frontend/
├── src/
│   ├── App.tsx                 # Root component, router setup
│   ├── main.tsx                # Entry point
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatWindow.tsx      # Main chat container
│   │   │   ├── MessageBubble.tsx   # Individual message (user/assistant)
│   │   │   ├── CitationBadge.tsx   # Clickable source reference
│   │   │   ├── ConfidenceBar.tsx   # Visual confidence indicator
│   │   │   ├── InputArea.tsx       # Message input with controls
│   │   │   └── AlternativePanel.tsx # Shows alternative theories
│   │   ├── library/
│   │   │   ├── DropZone.tsx        # Drag-and-drop file import
│   │   │   ├── DocumentGrid.tsx    # Library grid/list view
│   │   │   ├── DocumentCard.tsx    # Individual document card
│   │   │   ├── DocumentPreview.tsx # Document detail/preview
│   │   │   └── ImportProgress.tsx  # Batch import progress
│   │   ├── projects/
│   │   │   ├── ProjectList.tsx     # Project selector
│   │   │   └── ProjectForm.tsx     # Create/edit project
│   │   ├── architecture/
│   │   │   └── ComponentMap.tsx    # System architecture visualisation
│   │   ├── reports/
│   │   │   └── ReportBuilder.tsx   # Report configuration and export
│   │   ├── settings/
│   │   │   └── SettingsPanel.tsx   # Configuration UI
│   │   └── shared/
│   │       ├── Sidebar.tsx         # Navigation sidebar
│   │       ├── Layout.tsx          # Page layout wrapper
│   │       └── LoadingSpinner.tsx
│   ├── hooks/
│   │   ├── useQuery.ts            # Chat query hook
│   │   ├── useConversation.ts     # Conversation management
│   │   ├── useDocuments.ts        # Document library operations
│   │   └── useProjects.ts         # Project CRUD
│   ├── stores/
│   │   ├── uiStore.ts            # UI state (sidebar, active views)
│   │   └── appStore.ts           # Application state (current project)
│   ├── api/
│   │   └── client.ts             # API client (fetch to localhost backend)
│   └── types/
│       └── index.ts              # Shared TypeScript types
```

**Communication:** Frontend communicates with backend via HTTP REST API on localhost.
LLM responses stream via Server-Sent Events (SSE) for real-time token display.

### 2. Backend Layer (FastAPI)
```
backend/
├── main.py                      # FastAPI app creation, middleware, startup/shutdown
├── config.py                    # pydantic-settings configuration
├── dependencies.py              # FastAPI dependency injection
├── api/
│   ├── __init__.py
│   └── v1/
│       ├── __init__.py
│       ├── router.py            # Main API router aggregating all sub-routers
│       ├── documents.py         # POST/GET/DELETE documents, upload, batch import
│       ├── query.py             # POST query (main RAG endpoint)
│       ├── conversations.py     # CRUD conversations, messages, pinned facts
│       ├── projects.py          # CRUD projects
│       ├── reports.py           # Generate and export reports
│       ├── architecture.py      # System architecture endpoints
│       ├── settings.py          # Runtime settings, model selection
│       └── health.py            # Health check, system status
├── middleware/
│   ├── error_handler.py         # Global exception handling
│   └── logging.py               # Request/response logging
└── schemas/
    └── responses.py             # API response envelope schemas
```

**Role:** Thin adapter layer. All business logic delegated to `/core/`. FastAPI routes
call core functions, handle serialisation, manage HTTP concerns (status codes, streaming).

### 3. Core Library
```
core/
├── __init__.py
├── exceptions.py               # Exception hierarchy (SRAError base)
├── models/                     # Pydantic models (shared data structures)
│   ├── __init__.py
│   ├── document.py             # Document, Chunk, DocumentMetadata
│   ├── conversation.py         # Conversation, Message, PinnedFact
│   ├── query.py                # QueryRequest, QueryResponse, Citation, ConfidenceResult
│   ├── project.py              # Project
│   ├── architecture.py         # Component, Interface, SystemArchitecture
│   └── profile.py              # UserProfile, Preference
├── database/
│   ├── __init__.py
│   ├── connection.py           # SQLite connection manager (singleton)
│   ├── schema.py               # Table creation DDL
│   ├── migrations.py           # Schema versioning
│   └── repositories/           # Data access layer
│       ├── document_repo.py
│       ├── conversation_repo.py
│       ├── project_repo.py
│       └── profile_repo.py
├── ingest/
│   ├── __init__.py
│   ├── pipeline.py             # Main ingestion orchestrator
│   ├── detector.py             # File type detection and routing
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── base.py             # Abstract parser interface
│   │   ├── pdf_parser.py       # PyMuPDF-based PDF extraction
│   │   ├── image_parser.py     # Tesseract OCR + image handling
│   │   ├── code_parser.py      # tree-sitter code analysis
│   │   ├── text_parser.py      # Plain text, markdown, HTML
│   │   └── spreadsheet_parser.py # CSV, XLSX tabular data
│   ├── chunker.py              # Semantic chunking with overlap
│   └── embedder.py             # Local embedding generation
├── rag/
│   ├── __init__.py
│   ├── engine.py               # Main RAG orchestrator
│   ├── vector_search.py        # ChromaDB similarity search
│   ├── keyword_search.py       # BM25 keyword search
│   ├── fusion.py               # Reciprocal Rank Fusion
│   ├── reranker.py             # Context re-ranking
│   ├── context_builder.py      # Assemble LLM prompt with context
│   ├── llm_client.py           # Ollama API client (localhost only)
│   └── response_parser.py      # Extract citations from LLM response
├── validation/
│   ├── __init__.py
│   ├── pipeline.py             # Validation orchestrator
│   ├── confidence.py           # Confidence scoring algorithm
│   ├── hallucination.py        # Claim extraction and evidence checking
│   ├── cross_reference.py      # Multi-source comparison
│   └── source_tier.py          # Source quality classification
├── conversation/
│   ├── __init__.py
│   ├── manager.py              # Conversation lifecycle management
│   ├── memory.py               # Long-term memory and fact pinning
│   └── summariser.py           # Conversation summarisation for context compression
├── architecture/
│   ├── __init__.py
│   ├── extractor.py            # Component and interface extraction from documents
│   ├── mapper.py               # Relationship and connectivity mapping
│   └── visualiser.py           # Export architecture as structured data
├── profile/
│   ├── __init__.py
│   ├── tracker.py              # Implicit preference learning
│   └── adapter.py              # Adaptive prompt modification
├── reports/
│   ├── __init__.py
│   ├── generator.py            # Report compilation from multiple sources
│   ├── templates.py            # Report structure templates
│   └── exporter.py             # PDF, Markdown, JSON export
└── vector_store/
    ├── __init__.py
    └── chroma_client.py        # ChromaDB wrapper with collection management
```

### 4. Data Layer
```
data/
├── vectordb/                   # ChromaDB persistent storage
│   └── chroma.sqlite3          # ChromaDB's internal storage (auto-created)
├── sqlite/
│   └── sra.db                  # Application database
└── models/                     # Local LLM model files (if bundled)
```

## Data Flow Diagrams

### Document Ingestion Flow
```
User drops file(s) → Frontend DropZone
    → POST /api/v1/documents/upload (multipart)
    → backend/api/v1/documents.py
    → core/ingest/pipeline.py
        → core/ingest/detector.py (identify file type)
        → core/ingest/parsers/<type>_parser.py (extract text + metadata)
        → core/ingest/chunker.py (semantic chunking)
        → core/ingest/embedder.py (generate embeddings via Ollama)
        → core/vector_store/chroma_client.py (store vectors + metadata)
        → core/database/repositories/document_repo.py (store document record)
    → Return: DocumentMetadata with status
```

### Query Flow
```
User types question → Frontend InputArea
    → POST /api/v1/query { question, conversation_id }
    → backend/api/v1/query.py
    → core/rag/engine.py
        → core/conversation/manager.py (load conversation context)
        → core/rag/vector_search.py (ChromaDB semantic search)
        → core/rag/keyword_search.py (BM25 search)
        → core/rag/fusion.py (RRF merge results)
        → core/rag/reranker.py (re-rank top results)
        → core/rag/context_builder.py (assemble prompt)
        → core/rag/llm_client.py (send to Ollama, stream response)
        → core/rag/response_parser.py (extract citations)
        → core/validation/pipeline.py
            → core/validation/confidence.py (score response)
            → core/validation/hallucination.py (check claims)
            → core/validation/cross_reference.py (verify sources)
        → core/conversation/manager.py (save message + response)
    → SSE Stream: validated response with citations + confidence
```

## API Endpoints Reference

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/health | System health check |
| GET | /api/v1/settings | Current configuration |
| PUT | /api/v1/settings | Update configuration |
| POST | /api/v1/projects | Create project |
| GET | /api/v1/projects | List projects |
| GET | /api/v1/projects/{id} | Get project detail |
| DELETE | /api/v1/projects/{id} | Delete project |
| POST | /api/v1/documents/upload | Upload document(s) to project |
| POST | /api/v1/documents/batch | Batch import from directory path |
| GET | /api/v1/documents | List documents (filterable by project) |
| GET | /api/v1/documents/{id} | Document detail + chunks |
| DELETE | /api/v1/documents/{id} | Remove document and its chunks |
| PATCH | /api/v1/documents/{id}/tier | Update source quality tier |
| POST | /api/v1/query | Submit query (returns SSE stream) |
| POST | /api/v1/conversations | Create conversation |
| GET | /api/v1/conversations | List conversations (by project) |
| GET | /api/v1/conversations/{id} | Get conversation with messages |
| DELETE | /api/v1/conversations/{id} | Delete conversation |
| POST | /api/v1/conversations/{id}/pin | Pin a fact/finding |
| GET | /api/v1/conversations/{id}/pins | Get pinned facts |
| POST | /api/v1/reports/generate | Generate report for project |
| GET | /api/v1/reports/{id}/export | Export report (format param) |
| GET | /api/v1/architecture/{project_id} | Get system architecture |
| POST | /api/v1/architecture/{project_id}/extract | Trigger architecture extraction |
| GET | /api/v1/models | List available Ollama models |
