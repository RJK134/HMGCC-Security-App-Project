# Security Research Assistant

Smart Personal Assistant for Security Researchers.
HMGCC Co-Creation Challenge (CH-2026-001).

Helps security researchers characterise complex industrial machinery by ingesting, indexing,
and querying technical documentation using local LLM-powered retrieval-augmented generation.

**Fully offline. No internet required.**

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Ollama (with a local model installed)

### Backend
```bash
pip install -e ".[dev]"
uvicorn backend.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Project Structure
See `ARCHITECTURE.md` for system design and `REQUIREMENTS.md` for functional requirements.
