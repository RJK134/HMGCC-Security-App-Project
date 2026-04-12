# Demo Script — 20-Minute Pitch Day Presentation

## Minutes 0-3: Problem Statement

"National security organisations procure complex industrial machinery that must be
thoroughly assessed for vulnerabilities. Security researchers spend weeks — sometimes
months — gathering and understanding vast amounts of technical documentation about
every component in these systems.

Our tool eliminates that bottleneck using local AI."

## Minutes 3-6: Solution Overview

"The Security Research Assistant is a fully offline desktop tool that:
1. Ingests any technical document — PDFs, datasheets, code, images, spreadsheets
2. Indexes everything into a searchable knowledge base
3. Answers natural-language questions with cited, confidence-scored responses
4. Validates every answer against source material to prevent hallucination
5. Maps system architecture and generates professional reports

Everything runs locally. No internet. No cloud. Suitable for classified environments."

## Minutes 6-15: Live Demonstration

### Step 1: Import Documents (2 min)
- Open the Library page
- Drag sample documents (datasheet, firmware code, component CSV, security notes)
- Show the ingestion progress and tier assignment

### Step 2: Ask Questions (4 min)
- "What processor is used in this system?"
  → Show cited answer with confidence score
- "What communication interfaces are available?"
  → Show multi-source synthesis
- "Are there any security vulnerabilities?"
  → Show uncertainty handling and flagged claims

### Step 3: Architecture View (2 min)
- Click "Extract Architecture"
- Show the interactive component map
- Highlight extracted interfaces and protocols

### Step 4: Generate Report (1 min)
- Generate a Product Overview report
- Show the report viewer with TOC
- Export as PDF — open and show professional formatting

## Minutes 15-18: Technical Architecture

"Built with proven open-source technology:
- Ollama for local LLM inference (Mistral 7B)
- ChromaDB for vector search
- FastAPI backend with 234 automated tests
- Tauri + React desktop application
- Hybrid search: vector similarity + BM25 keyword with Reciprocal Rank Fusion"

## Minutes 18-20: Roadmap and Q&A

"Phase 2 opportunities: autonomous data collection, ML schematic analysis,
multi-user collaboration, MITRE ATT&CK integration.

Questions?"
