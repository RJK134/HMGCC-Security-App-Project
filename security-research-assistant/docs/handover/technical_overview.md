# Technical Overview — HMGCC Handover

## System Architecture

The SRA is a three-tier local application:

```
[Tauri Desktop App] → [FastAPI Backend] → [Ollama LLM + ChromaDB + SQLite]
```

All communication is `localhost` only. Zero network egress.

## Technology Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| LLM | Ollama + Mistral 7B | Offline-capable, quantised for laptop CPU |
| Embeddings | nomic-embed-text via Ollama | Offline, good quality-to-size ratio |
| Vector DB | ChromaDB (embedded) | No server process, Python-native, persistent |
| Backend | Python 3.11+ / FastAPI | Rapid development, strong typing, async support |
| Frontend | Tauri + React + TypeScript | Native desktop feel, small bundle, secure |
| Document parsing | PyMuPDF, Tesseract, tree-sitter | Industry-standard, offline-capable |
| Database | SQLite (WAL mode) | Zero-config, robust, single-file backup |

## Module Responsibilities

| Module | Purpose |
|--------|---------|
| `core/ingest/` | File detection, 5 parsers (PDF, image, code, text, spreadsheet), semantic chunking, embedding |
| `core/rag/` | Vector search, BM25 keyword search, RRF fusion, reranking, context building, LLM generation, response parsing |
| `core/validation/` | Source tier classification, confidence scoring (0-100), hallucination detection, cross-referencing |
| `core/conversation/` | Conversation CRUD, incremental summarisation, pinned facts, context reconstruction |
| `core/architecture/` | LLM-based component extraction, graph mapping, summary generation |
| `core/reports/` | 4 report templates, LLM-assisted section generation, PDF/MD/JSON/HTML export |
| `core/profile/` | Preference tracking, adaptive prompting, proactive notifications |
| `backend/` | FastAPI thin layer: routes, middleware, dependency injection |
| `frontend/` | Tauri + React: chat, library, architecture, reports, settings |

## How to Extend

- **Add a parser:** Create a new class in `core/ingest/parsers/` extending `BaseParser`, register in `pipeline.py`
- **Swap LLM model:** Change `SRA_OLLAMA_MODEL` in config, or use `ollama pull <model>`
- **Add a report type:** Add template to `core/reports/templates.py`, sections are auto-generated
- **Add an API endpoint:** Create a new file in `backend/api/v1/`, register in `router.py`

## Known Technical Debt

1. Python 3.14 `html.entities` stdlib regression affects PyMuPDF and reportlab — PDF operations require Python 3.11-3.13
2. BM25 index is rebuilt on chunk count change — could be optimised with incremental updates
3. Reranker makes an LLM call per query — expensive, currently disabled by default for speed
4. Frontend lacks comprehensive test suite (Vitest configured but tests not written)
5. No database migration system — schema changes require manual intervention
