# Security Research Assistant v0.1.0

## Release Date
2026-04-12

## Overview
Initial release of the Security Research Assistant MVP for HMGCC Co-Creation Challenge CH-2026-001.

## Features

### Document Ingestion
- Multi-modal import: PDF, images (with OCR), source code (with tree-sitter parsing), plain text, spreadsheets
- Drag-and-drop and batch directory import
- Semantic chunking preserving document structure
- Source quality tier classification (4 tiers)

### Conversational Query
- Natural-language questions with cited, confidence-scored answers
- Hybrid search: vector similarity + BM25 keyword with Reciprocal Rank Fusion
- LLM-based re-ranking for improved relevance
- Real-time streaming responses via SSE

### Response Validation
- Confidence scoring (0-100) based on source quality and coverage
- Hallucination detection: flags unsupported and contradicted claims
- Cross-reference engine: detects agreements and disagreements between sources
- Every response passes through validation before display

### Conversational Memory
- Persistent conversations across sessions spanning weeks
- Incremental summarisation for context compression
- Pinned facts as long-term memory (always included in context)
- Multiple concurrent investigation threads

### Architecture Characterisation
- Extract components, interfaces, protocols, and software from documents
- Build interactive component graph with colour-coded groups
- LLM-generated architecture summaries
- Export as structured JSON

### Report Generation
- Four report types: Product Overview, Component Analysis, System Architecture, Investigation Summary
- Export: PDF (with cover page, TOC), Markdown, JSON, HTML
- Citations and confidence notes in all formats

### User Profiling
- Learns query patterns, detail preferences, and format preferences
- Adapts system prompts based on learned behaviour
- Proactive notifications when new documents match investigation topics
- Suggested follow-up queries

### Offline Operation
- Fully offline: Ollama for local LLM inference, ChromaDB embedded vector DB
- No internet, no telemetry, no cloud dependencies
- Data export/import for air-gapped migration

## System Requirements
- Windows 10/11 (x64) or Linux (x64, Ubuntu 20.04+)
- 16 GB RAM recommended (8 GB minimum)
- 20 GB free disk space (including models)
- Optional: NVIDIA GPU with 6 GB+ VRAM for faster inference

## Known Limitations
- OCR accuracy on handwritten annotations varies (60-80%)
- First query after ingestion may be slower while indices warm up
- Maximum recommended dataset size: ~5000 documents per project
- LLM response quality depends on model choice and quantisation level
- PDF parsing requires PyMuPDF (may have issues on Python 3.14+)

## Technology Stack
Python 3.11+ | FastAPI | Ollama | ChromaDB | SQLite | Tauri | React | TypeScript | Tailwind CSS

## Test Results
- 234 Python unit/integration tests passing
- 11 tests skipped (Python 3.14 html.entities compatibility)
- Frontend: TypeScript strict mode, Vite production builds clean

## Installation
See docs/user_guide.md for detailed installation instructions.
