# Architecture

## System Overview

```
+------------------------------------------------------+
|              DESKTOP APP (Tauri + React)              |
|  +-------------+  +--------------+  +-------------+  |
|  |  Chat UI    |  | Data Import  |  |  Reports    |  |
|  |  (React)    |  | Drag & Drop  |  |  Export     |  |
|  +------+------+  +------+-------+  +------+------+  |
+---------|--------------|--------------------|--------+
          |              |                    |
+---------v--------------v--------------------v--------+
|             PYTHON BACKEND (FastAPI)                  |
|  +------------+ +--------------+ +----------------+  |
|  | RAG Engine | |  Doc Parser  | | Summary Gen    |  |
|  | (LlamaIdx) | |  Pipeline    | | & Validation   |  |
|  +-----+------+ +------+------+ +-------+--------+  |
|        |               |                 |           |
|  +-----v---------------v-----------------v--------+  |
|  |            Orchestration Layer                  |  |
|  |   - Query routing  - Confidence scoring        |  |
|  |   - Source tracking - Hallucination detection   |  |
|  +-----+--------------------------------------+---+  |
+--------|--------------------------------------|------+
         |                                      |
+--------v------------------+  +----------------v------+
|   LOCAL LLM (Ollama)      |  |   DATA STORES         |
|  - Mistral/Llama 3        |  |  +------------------+ |
|  - Embedding model        |  |  | ChromaDB         | |
|                           |  |  | (Vector Store)   | |
|                           |  |  +------------------+ |
|                           |  |  | SQLite           | |
|                           |  |  | (Conversations,  | |
|                           |  |  |  Profiles, Meta) | |
|                           |  |  +------------------+ |
+---------------------------+  +-----------------------+
```

## Layers

### Frontend (Tauri + React + TypeScript)
- Desktop app shell with native window, menu bar, system tray
- Views: Projects, Chat, Library, Settings
- Drag-and-drop file ingestion
- Chat interface with source citations, confidence badges, alternative theories
- Component architecture diagram viewer (React Flow)

### Backend (FastAPI)
- REST API serving the frontend
- Orchestrates all core modules
- Manages request lifecycle and error handling
- API versioned under `/api/v1/`

### Core Library
- **ingest/**: Multi-modal document parsing (PDF, images, code, datasheets)
- **rag/**: Hybrid search (vector + BM25), query processing, response generation
- **conversation/**: Conversation CRUD, context window management, long-term memory
- **validation/**: Source quality tiers, confidence scoring, hallucination detection
- **architecture/**: Component extraction, relationship mapping, system diagrams
- **profile/**: User behaviour tracking, adaptive prompts, proactive suggestions
- **reports/**: Template-based report generation, PDF/Markdown/JSON export

### Data Stores
- **ChromaDB**: Embedded vector database for document embeddings
- **SQLite**: Conversations, messages, documents, user profiles, sources, metadata
- **Filesystem**: Raw ingested files, model files, exported reports

## Key Design Decisions
- **Offline-first**: Zero network calls. All inference, embedding, and storage local.
- **Hybrid search**: Vector similarity + BM25 keyword search with Reciprocal Rank Fusion.
- **Validation pipeline**: Every LLM response validated before display.
- **Source provenance**: Full metadata chain from raw file to displayed citation.
