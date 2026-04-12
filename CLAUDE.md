# HMGCC Security App Project

## Overview
HMGCC Co-Creation Challenge (CH-2026-001): Smart Personal Assistant for Security Researchers.
Budget: £60,000 | Duration: 12 weeks | Target: TRL-6 | Competition close: 2026-05-07

Builds a fully offline tool that helps security researchers characterise complex industrial machinery
by ingesting, indexing, and querying technical documentation using local LLM-powered RAG.

**Key Constraint: Fully offline operation. No internet calls. No telemetry. OFFICIAL classification suitable.**

## Repository Structure
```
HMGCC-Security-App-Project/
├── CLAUDE.md                          # This file
├── HMGCC Security SPA .md            # Full challenge specification
├── HMGCC Security SPA .txt           # Specification (text copy)
├── security-research-assistant/       # Application source code
│   ├── CLAUDE.md                     # Dev guide for the application
│   ├── ARCHITECTURE.md               # System architecture and design
│   ├── REQUIREMENTS.md               # Functional and non-functional requirements
│   ├── CONVENTIONS.md                # Coding standards
│   ├── TASKS.md                      # Sprint task tracker
│   ├── pyproject.toml                # Python dependencies
│   ├── package.json                  # Frontend dependencies
│   ├── backend/                      # FastAPI application
│   ├── core/                         # Core library (RAG, ingestion, validation, etc.)
│   ├── frontend/                     # Tauri + React desktop app
│   ├── data/                         # Local data storage (vectordb, sqlite, models)
│   ├── tests/                        # Test suites
│   └── docs/                         # Documentation
```

## Tech Stack
- **Backend**: Python 3.11+, FastAPI, Uvicorn, Pydantic
- **LLM**: Ollama (Mistral/Llama 3, local inference only)
- **Embeddings**: all-MiniLM-L6-v2 or nomic-embed-text
- **Vector DB**: ChromaDB (embedded)
- **SQL DB**: SQLite
- **Document Processing**: PyMuPDF, Tesseract OCR, tree-sitter
- **Frontend**: Tauri + React + TypeScript
- **Testing**: pytest, Vitest

## Build Phases
1. **Foundation** (Weeks 1-2): Project scaffolding, FastAPI, Ollama, ChromaDB, SQLite, ingestion pipeline
2. **Core Intelligence** (Weeks 3-5): RAG engine, hybrid search, conversation memory, validation engine
3. **User Interface** (Weeks 5-7): Tauri desktop app, chat UI, drag-and-drop import
4. **Advanced Features** (Weeks 7-10): Architecture mapping, reports, user profiling
5. **Testing & Deployment** (Weeks 10-12): Integration tests, offline packaging, installer

## Commands
```bash
# Backend
cd security-research-assistant
pip install -e ".[dev]"
uvicorn backend.main:app --reload

# Frontend
cd security-research-assistant/frontend
npm install
npm run dev

# Tests
cd security-research-assistant
pytest
```

## Conventions
- See `security-research-assistant/CONVENTIONS.md` for full coding standards
- Conventional commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`
- All data stays local — zero network calls enforced at every layer
- Every LLM response passes through validation before display
