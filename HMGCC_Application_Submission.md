# HMGCC Co-Creation Challenge Application
## Smart Personal Assistant for Security Researchers
### Challenge ID: CH-2026-001

---

**Applicant:** Future Horizons Education
**Date:** 14 April 2026
**Contact:** [Contact details to be inserted prior to submission]
**Submission Deadline:** 7 May 2026
**Briefing Call:** 17 April 2026 (attendance confirmed)
**Pitch Day:** 2 June 2026 (live demonstration prepared)

---

## 1. Executive Summary

Future Horizons Education presents a **working prototype** of the Smart Personal Assistant for Security Researchers — a fully offline desktop tool that helps security researchers characterise complex industrial machinery by ingesting, indexing, and querying technical documentation using local LLM-powered Retrieval-Augmented Generation (RAG).

We have built a functioning TRL-6 system comprising approximately **13,000 lines of production code** across 175 source files, validated through **245 automated tests** (234 passing, 11 skipped for Python version compatibility), a structured internal security review, performance benchmarks, and **three rounds of structured user testing** using AI-simulated security researcher personas.

The tool runs entirely on a standard laptop with no internet connection. It ingests multi-modal technical documentation (PDFs, images, schematics, source code, datasheets, spreadsheets), indexes it using hybrid semantic and keyword search, and enables natural-language querying with cited, confidence-scored, and hallucination-checked responses. It maintains conversational memory across weeks of investigation, adapts to the researcher's working style, extracts system architecture from imported documents, and generates structured reports.

**All 8 essential requirements and all 4 desirable requirements** specified in the challenge have been implemented and tested.

We are applying for the full £60,000 budget to take this working prototype through a 12-week programme of hardening, field testing with HMGCC-provided data, security accreditation preparation, and packaging for deployment in classified environments.

---

## 2. The Problem

National security organisations procure complex industrial machinery that must be thoroughly checked for security vulnerabilities. Security researchers conduct detailed tear-downs of software, hardware, and data components. The bottleneck is the initial research phase — finding, indexing, and understanding vast amounts of open-source technical information about complex industrial control systems at a micro-component level.

A typical investigation involves hundreds of components, each with datasheets, schematics, firmware code, forum discussions, and vendor manuals. Researchers currently manage this information manually using file folders, spreadsheets, and personal notes. There is no tool that can ingest all of this heterogeneous data, index it, and allow the researcher to query it conversationally with confidence in the reliability of the answers.

This is the problem our tool solves.

---

## 3. Our Solution: The Security Research Assistant (SRA)

The Security Research Assistant is a desktop application that runs entirely offline on a standard laptop. It provides six core capabilities:

### 3.1 Multi-Modal Document Ingestion
The researcher drags and drops technical documents into the tool. The ingestion pipeline automatically detects file types and routes them to specialised parsers:

- **PDFs:** Text extraction via PyMuPDF with table and image handling
- **Images and Schematics:** Optical Character Recognition via Tesseract OCR
- **Source Code:** Abstract Syntax Tree parsing via tree-sitter (C, Python, assembly, and more)
- **Datasheets:** Structured data extraction from tabular formats
- **Text, Markdown, HTML:** Standard text processing
- **Spreadsheets:** CSV and XLSX parsing into searchable text

Documents are semantically chunked (preserving headings, sections, and tables), embedded using local embedding models, and stored in a vector database with full provenance metadata.

### 3.2 Intelligent Conversational Search
The researcher asks natural-language questions about their imported data and receives conversational, well-grounded answers. The RAG engine uses:

- **Hybrid search:** Vector similarity (ChromaDB) for conceptual matching combined with BM25 keyword search for exact terms (part numbers, protocol names), fused via Reciprocal Rank Fusion
- **LLM-based re-ranking:** Retrieved passages are re-scored by the local language model for relevance
- **Token-aware context assembly:** The most relevant passages are assembled into a prompt that respects the model's context window
- **Streaming responses:** Answers stream token-by-token for immediate feedback

### 3.3 Response Validation and Anti-Hallucination
Every LLM response passes through a validation pipeline before reaching the researcher:

- **Confidence scoring (0-100):** Based on source coverage, source quality tiers, claim corroboration, and consistency
- **Hallucination detection:** Each claim in the response is cross-checked against retrieved source chunks; unsupported claims are flagged
- **Cross-referencing:** When multiple sources discuss the same topic, agreements and disagreements are highlighted
- **Source citations:** Every answer includes clickable citation badges linking to the specific source document and page

### 3.4 Conversational Memory
Investigations span weeks. The tool maintains context across sessions:

- **Conversation summaries:** Older messages are automatically summarised to fit within the LLM context window
- **Pinned facts:** The researcher can pin key discoveries that persist as permanent context
- **Multi-thread support:** Multiple concurrent investigation threads per project
- **Session resumption:** Returning after days or weeks reconstructs context automatically from summary, pinned facts, and recent messages

### 3.5 System Architecture Extraction
From imported datasheets, schematics, and manuals, the tool extracts:

- Component names and types (processors, memory, sensors, fuses)
- Interface types (SPI, I2C, UART, GPIO, Ethernet)
- Communication protocols (Modbus, CAN, proprietary)
- Software components (OS, firmware versions, libraries)

These are assembled into an interactive component relationship graph with a natural-language architecture summary.

### 3.6 Report Generation
The tool generates structured reports from the investigation data:

- **Product Overview Report** — comprehensive summary of the assessed product
- **System Architecture Report** — component hierarchy, interfaces, and protocols
- **Investigation Summary** — key findings, conversations, and pinned facts
- **Vulnerability Surface Summary** — identified attack surfaces and information gaps

Reports export as PDF, Markdown, HTML, or JSON.

---

## 4. Working Prototype Demonstration

### What Exists Today

The prototype is a fully functional desktop application with the following verified capabilities:

| Feature | Status | Evidence |
|---------|--------|----------|
| Multi-modal document ingestion (6 types, 30+ extensions) | Working | 245 automated tests |
| Hybrid search (vector + keyword + RRF) | Working | 6 test modules |
| Confidence scoring (0-100) | Working | Algorithm validated, 3 user test rounds |
| Hallucination detection | Working | Cross-reference against source chunks |
| Source citations with clickable badges | Working | User testing verified |
| Conversational memory (weeks-long) | Working | Conversation persistence verified |
| System architecture extraction | Working | Component graph generation |
| Report generation (4 formats) | Working | PDF, Markdown, HTML, JSON export |
| User profiling and adaptation | Working | Preference tracking and adaptive prompting |
| Non-English data support | Working | Translation pipeline via local LLM |
| First-run setup wizard | Working | User testing verified |
| Classification footer ("OFFICIAL") | Working | Present on every page |
| Fully offline operation | Verified | Zero external network calls confirmed |

### Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Local LLM | Ollama (Mistral 7B / Llama 3 8B) | Offline inference, strong reasoning, model-swappable |
| Embeddings | nomic-embed-text via Ollama | Local embedding generation, no cloud dependency |
| Vector DB | ChromaDB (embedded) | Lightweight, no server process, Python-native |
| Backend | Python 3.11+ with FastAPI | Orchestration, RAG pipeline, REST API |
| Frontend | Tauri + React 18 + TypeScript | Native desktop feel, small footprint, cross-platform |
| Document Processing | PyMuPDF, Tesseract OCR, tree-sitter | Multi-modal parsing, well-maintained open source |
| Relational DB | SQLite | Conversations, user profiles, document metadata |
| Search | Hybrid: ChromaDB vector + rank-bm25 keyword | Best of both for security research queries |

### Architecture

```
[Tauri Desktop App (React/TypeScript)]
            |
            v
[FastAPI Backend (Python)]
    |-- Document Ingestion Pipeline
    |     |-- PDF Parser (PyMuPDF)
    |     |-- Image/OCR (Tesseract + Pillow)
    |     |-- Code Parser (tree-sitter)
    |     |-- Semantic Chunker
    |     +-- Embedding Generator
    |-- RAG Query Engine
    |     |-- Hybrid Search (Vector + BM25)
    |     |-- Re-ranker
    |     |-- Context Assembler
    |     +-- LLM Interface (Ollama)
    |-- Validation Engine
    |     |-- Confidence Scorer
    |     |-- Hallucination Detector
    |     +-- Source Cross-Referrer
    |-- Conversation Manager
    |     |-- Session History (SQLite)
    |     |-- Context Reconstructor
    |     +-- Long-term Memory (Pinned Facts)
    +-- User Profile Engine
          |-- Preference Tracker
          +-- Adaptive Prompting
            |
    +-------+-------+
    v       v       v
[ChromaDB] [SQLite] [Ollama]
```

All components run locally. The only network traffic is between the frontend and the local backend on localhost.

---

## 5. Requirements Compliance

### Essential Requirements — 8/8 Complete

| Requirement | How We Meet It |
|-------------|---------------|
| **ER-01: System Architecture Understanding** | `core/architecture/` module extracts components, interfaces, protocols, and software from imported documents. Builds interactive component relationship graphs. Generates natural-language architecture summaries. |
| **ER-02: Response Validation & Anti-Hallucination** | Every LLM response passes through `core/validation/` pipeline: confidence scoring, hallucination detection (claim vs. evidence comparison), and cross-referencing. No raw LLM output reaches the user. |
| **ER-03: Multi-Modal Input Characterisation** | `core/ingest/parsers/` supports 6 document types (PDF, images, code, text, spreadsheets, schematics) across 30+ file extensions. OCR for images and schematics. tree-sitter for code parsing. |
| **ER-04: Source Verification & Cross-Referencing** | 4-tier source quality classification (Manufacturer > Academic > Trusted Forum > Unverified). Cross-reference engine highlights agreements and disagreements across sources. User-assignable tiers. |
| **ER-05: Confidence Scoring** | 0-100 confidence score on every response based on source coverage, quality tiers, claim support, and consistency. Human-readable explanations. Low scores suggest what additional data might help. |
| **ER-06: Fully Offline Operation** | Entire stack runs locally: Ollama for LLM inference, ChromaDB for vectors, SQLite for data, Tauri for desktop. Zero external API calls. Verified by network monitoring. |
| **ER-07: Intelligent Search & Chat** | Chat-like interface with streaming responses, markdown rendering, code highlighting, inline citation badges, confidence bars. Hybrid search (vector + keyword + RRF) for comprehensive retrieval. |
| **ER-08: Conversational Memory** | SQLite-backed conversations persist across restarts. Automatic summarisation of older messages. Pinned facts for key discoveries. Context reconstruction on session resume. Multiple concurrent threads. |

### Desirable Requirements — 4/4 Complete

| Requirement | How We Meet It |
|-------------|---------------|
| **DR-01: User Profiling & Adaptive Behaviour** | `core/profile/` tracks query patterns, preferred detail levels, and topic interests. Adaptive prompting adjusts LLM system prompts based on learned preferences. Proactive suggestions surface related documents. |
| **DR-02: Non-English Data Support** | `core/ingest/translator.py` detects non-English content during ingestion and translates via local LLM. Original text preserved alongside translation. Search works across translated content. |
| **DR-03: Cultural Bias Mitigation** | Prompt engineering in `core/rag/context_builder.py` instructs the LLM to present information neutrally and surface multiple perspectives when sources from different regions conflict. |
| **DR-04: Offline Update Mechanism** | Data export/import for version migration. Model swap capability (load new LLM model files from USB). Clear versioning. Update scripts and documentation provided. |

---

## 6. Feasibility

### Technical Credibility

The prototype is built on a **proven, mature open-source stack**. Every component has been selected for offline compatibility, active maintenance, and community support:

- **Ollama** — widely used local LLM runtime, supports 100+ models, active development
- **ChromaDB** — embedded vector database, Python-native, no server dependency
- **FastAPI** — production-grade Python web framework, async-capable
- **Tauri** — modern desktop framework, smaller footprint than Electron, cross-platform
- **PyMuPDF** — fastest Python PDF library, no external dependencies
- **tree-sitter** — industry-standard code parsing (used by GitHub, Neovim, Helix)

### Risks Identified and Mitigated

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| LLM quality offline (quantised models) | Medium | Medium | Model-swappable architecture; tested with Mistral 7B and Llama 3 8B; prompt engineering optimised for local models |
| OCR accuracy on schematics | Medium | Low | Multi-strategy: OCR + image embedding for visual retrieval; manual annotation support; accuracy documented (85-95% printed, 60-80% handwritten) |
| Performance on laptop hardware | Low | Medium | Response streaming for immediate feedback; rAF token batching; configurable chunk sizes; GPU acceleration when available |
| 12-week timeline | Low | High | Working prototype already exists; 12-week programme focuses on hardening and field testing, not greenfield development |

### TRL-6 Achievability

TRL-6 requires "system/subsystem model or prototype demonstration in a relevant environment." Our prototype:

- Is a **complete, functioning system** (not a subsystem or mockup)
- Has been **tested with representative ICS data** (Modbus protocol specs, CAN transceiver datasheets, STM32 technical references, firmware code, security assessment notes)
- Operates in the **target environment** (offline laptop)
- Has undergone **three rounds of structured user testing** with simulated security researcher personas

---

## 7. Desirability

### Beyond Essential Requirements

We have implemented **all 4 desirable requirements** in addition to the 8 essential requirements. This includes:

- **User profiling and adaptive behaviour** — the tool learns the researcher's preferences and adapts
- **Non-English data support** — translation pipeline for international datasheets and forum posts
- **Cultural bias mitigation** — neutral presentation of information from diverse sources
- **Offline update mechanism** — data export/import and model swapping without internet

### Dual-Use Potential

The SRA architecture is domain-agnostic. While built for security research, the same tool can serve:

- **Defence supply chain assessment** — evaluating components from international suppliers
- **Critical infrastructure audit** — characterising SCADA/ICS systems
- **Commercial product security** — pre-market security evaluation for manufacturers
- **Academic research** — any domain requiring systematic literature review with source validation
- **Intelligence analysis** — multi-source information synthesis with provenance tracking

### Ambition Level

This is not an incremental improvement to existing tools. It represents a **significant capability leap**: combining local LLM inference, hybrid search, hallucination detection, confidence scoring, and conversational memory in a single offline package. No comparable open-source or commercial tool exists that combines all of these capabilities for air-gapped deployment.

---

## 8. Viability

### Exploitation Route

**Phase 1 (This Project):** Working prototype for HMGCC evaluation and field testing.

**Phase 2 (Post-Project, 16-24 weeks, estimated £95,000-135,000):**
- Autonomous data collection pipeline (pre-download to USB for air-gapped transfer)
- ML-based schematic analysis (computer vision beyond OCR)
- Multi-user collaboration with role-based access control
- MITRE ATT&CK for ICS framework integration
- Hardware acceleration optimisation (CUDA/ROCm)
- ICS domain fine-tuning of base models

**Phase 3 (Commercial):**
- Licensed deployment to allied nations' security services
- Commercial SaaS version for non-classified product security assessment
- Plugin marketplace for domain-specific extensions
- Training and consultancy services

### Commercial Thinking

The underlying technology — offline RAG with validation — has applications far beyond security research. Any domain requiring reliable, cited answers from a private document corpus can benefit: legal discovery, medical research, regulatory compliance, engineering analysis.

Future Horizons Education is positioned to develop this as an educational and professional development platform, with the HMGCC challenge providing the initial use case and validation.

---

## 9. Budget

### £60,000 Allocation (12 Weeks)

| Category | Amount | Description |
|----------|--------|-------------|
| **Personnel** | £48,000 | 1-2 FTE developers: hardening, field testing, security accreditation prep |
| **Infrastructure & Tooling** | £4,000 | Test hardware, Ollama model hosting, development tools |
| **Testing & Validation** | £4,000 | Domain expert review, structured user testing with HMGCC data |
| **Packaging & Documentation** | £2,000 | Windows/Linux installers, user guides, admin documentation |
| **Contingency** | £2,000 | Unforeseen technical challenges, additional testing |
| **Total** | **£60,000** | |

### Value for Money

The working prototype represents a significant head start. The £60,000 funds a hardening and deployment programme, not a greenfield build. Key activities:

- Field testing with HMGCC-provided representative data
- Security hardening for classified deployment (data-at-rest encryption, audit logging)
- Cross-platform installer testing (Windows and Linux clean VMs)
- Performance optimisation on target hardware
- User acceptance testing with HMGCC security researchers
- Comprehensive documentation and handover

---

## 10. Delivery Plan

### 12-Week Programme (July - September 2026)

| Week | Phase | Deliverable |
|------|-------|-------------|
| 1-2 | **Onboarding & Data Setup** | Receive HMGCC test data; configure tool for representative datasets; initial field testing |
| 3-4 | **Security Hardening** | Data-at-rest encryption (SQLCipher evaluation); filename sanitisation; audit logging; configurable classification markings; security testing |
| 5-6 | **Performance Optimisation** | GPU acceleration profiling; chunk size tuning for target datasets; response latency optimisation; memory footprint reduction |
| 7-8 | **User Acceptance Testing** | Structured UAT sessions with HMGCC security researchers; bug fixing; UI/UX refinement based on real-world feedback |
| 9-10 | **Integration Testing** | Full end-to-end testing with 2000+ document datasets; offline deployment verification; cross-platform testing (Windows + Linux) |
| 11 | **Packaging & Documentation** | Windows NSIS installer; Linux AppImage; bundled Ollama with default model; user guide; admin guide; API documentation |
| 12 | **Handover** | Final delivery to HMGCC; live demonstration; technical handover; Phase 2 roadmap presentation |

---

## 11. Team

### Future Horizons Education

Future Horizons Education is a technology-focused organisation specialising in the application of artificial intelligence, machine learning, and advanced software engineering to education, professional development, and research challenges. The organisation combines deep technical capability in AI systems with a commitment to making complex technology accessible and practical for end users.

### Key Personnel

**Richard Knapp — Technical Lead and Co-Founder**

Richard Knapp leads the technical delivery at Future Horizons Education, bringing expertise across AI/ML engineering, full-stack software development, and systems architecture. His experience encompasses:

- **AI and Machine Learning:** Design and deployment of local LLM inference systems, Retrieval-Augmented Generation (RAG) architectures, embedding model optimisation, vector database implementation, and prompt engineering for domain-specific applications
- **Software Engineering:** Production-grade development in Python (FastAPI, Pydantic, SQLAlchemy), TypeScript/React, desktop application frameworks (Tauri, Electron), and database systems (SQLite, ChromaDB, PostgreSQL)
- **Security-Aware Development:** Building offline-first systems for restricted environments, implementing data classification controls, network isolation verification, and secure software development lifecycle practices
- **Systems Integration:** End-to-end delivery from requirements analysis through architecture design, implementation, testing, and deployment packaging

Richard has led the development of the Security Research Assistant prototype from concept through to working system, overseeing the architecture, RAG pipeline design, validation engine, and deployment tooling. He is the primary technical contact for the 12-week delivery programme.

**Lyndon Shirley — Strategy, Quality Assurance and Co-Founder**

Lyndon Shirley oversees strategic direction, quality assurance, and stakeholder engagement at Future Horizons Education. His experience includes:

- **Product Strategy:** Translating complex user requirements into deliverable product specifications, roadmap planning, and stakeholder communication for technical projects
- **Quality Assurance and Testing:** Structured testing methodologies, user acceptance testing design, performance benchmarking, and validation of AI system outputs against ground truth
- **Education and Professional Development:** Curriculum design for technology-focused training programmes, knowledge transfer frameworks, and technical documentation for diverse audiences
- **Programme Management:** Delivery assurance across multi-phase projects, risk management, budget oversight, and milestone tracking for funded programmes
- **Domain Engagement:** Bridging the gap between technical implementation and real-world user needs, ensuring that tools are designed for practical adoption rather than theoretical demonstration

Lyndon has led the quality assurance and user testing programme for the SRA, designing the structured multi-round testing methodology with simulated security researcher personas and overseeing the documentation and handover preparation.

### Organisational Capabilities

| Capability | Evidence |
|-----------|----------|
| AI/ML Engineering | Working RAG system with hybrid search, confidence scoring, hallucination detection |
| Full-Stack Development | 13,000+ lines of Python + TypeScript, FastAPI backend, React/Tauri desktop app |
| Offline Systems | Fully air-gapped architecture verified by security review |
| Testing and QA | 245 automated tests, 3 rounds of structured user testing, security audit |
| Documentation | Comprehensive handover pack: user guide, admin guide, API docs, demo script |
| Delivery Track Record | Working prototype delivered on specification with all requirements met |

---

## 12. Quality Assurance

### Testing Approach

| Level | Coverage | Tool |
|-------|----------|------|
| **Unit Tests** | 234 tests across 34 modules | pytest |
| **Integration Tests** | End-to-end RAG pipeline | pytest + fixtures |
| **Security Audit** | Network isolation, SQL injection, path traversal, data-at-rest | Manual review |
| **Performance Benchmarks** | Query latency, ingestion throughput, memory usage | Automated benchmarks |
| **User Testing** | 3 rounds with 5 simulated researcher personas | Structured test scripts |
| **Offline Verification** | Zero external network calls | Network traffic monitoring |

### User Testing History

Three rounds of structured user testing have been conducted with simulated security researcher personas:

**Round 1:** Initial feature validation — identified 10 bugs across citation display, confidence scoring, and UI feedback. All fixed.

**Round 2:** Regression testing — verified Round 1 fixes, identified 10 additional issues across error handling, pagination, and source tier management. All fixed.

**Round 3:** Verification testing with 5 specialist testers — identified 3 new critical bugs (response persistence, streaming regression) plus confirmed fixes for prior issues. All critical bugs fixed; 1 issue (report grounding) mitigated with citation validation.

### Internal Security Review (2026-04-12)

Structured security review covering:
- Network isolation: **PASS** (localhost only)
- Secrets and credentials: **PASS** (none hardcoded)
- SQL injection: **PASS** (parameterised queries)
- Path traversal: **PASS** (with recommendation for additional sanitisation)
- Dependency review: **PASS** (all MIT/Apache 2.0/BSD licensed)
- 5 hardening recommendations documented for classified deployment

---

## 13. Intellectual Property

The Security Research Assistant prototype is built entirely on open-source technologies (MIT, Apache 2.0, and BSD licensed). No proprietary third-party dependencies or licence fees are required.

Intellectual property arrangements for code developed under the £60,000 funding will follow the terms specified in the HMGCC Co-Creation Challenge agreement. Future Horizons Education is open to granting HMGCC a perpetual, non-exclusive licence to use, modify, and deploy the delivered tool, while retaining the right to develop the underlying technology for commercial and educational applications outside classified environments.

---

## 14. Key Dates and Milestones

| Date | Event | Our Plan |
|------|-------|----------|
| 17 April 2026 | Briefing Call (10am) | Attend; submit clarifying questions by deadline |
| 28 April 2026 | Answers Published | Review and incorporate into final submission |
| 7 May 2026 | Submission Closes (5pm) | Submit via HMGCC Co-Creation website |
| 22 May 2026 | Applicant Notification | Await outcome |
| 2 June 2026 | Pitch Day | Live demonstration of working prototype (20-minute presentation with demo script prepared) |
| 8 June 2026 | Pitch Outcomes | Await outcome |
| 12 June 2026 | Onboarding Call | MS Teams onboarding with HMGCC team |
| July 2026 | Project Start | Begin 12-week hardening and deployment programme |

---

## 15. Appendix A: Known Limitations and Mitigations

| Limitation | Mitigation | Severity |
|-----------|-----------|----------|
| Quantised LLM models (7B) may miss nuance compared to larger models | Architecture supports model swapping; 13B+ models recommended for complex analysis | Medium |
| OCR accuracy: 85-95% printed text, 60-80% handwritten annotations | Multi-strategy parsing; manual review flagged for low-confidence OCR | Low |
| Architecture extraction is text-dependent; misses unlabelled components | Researcher can manually annotate; LLM identifies gaps | Low |
| Confidence scoring is heuristic-based, not statistically calibrated | Clear explanation of scoring methodology; researcher exercises judgement | Medium |
| Recommended maximum ~5,000 documents per project | Sufficient for typical ICS assessment; pagination and archival for larger sets | Low |
| Single-user design; no authentication or RBAC | Appropriate for individual researcher workflow; Phase 2 adds multi-user | Low |
| Data at rest is unencrypted in SQLite/ChromaDB | OS-level encryption recommended for immediate deployment; SQLCipher evaluation planned during 12-week programme (weeks 3-4) | Medium |

---

## 16. Appendix B: Future Roadmap (Phase 2)

| Enhancement | Description | Estimated Effort |
|-------------|-------------|-----------------|
| Autonomous Data Collection | Pre-download pipeline for air-gapped transfer via USB | 4 weeks |
| ML-Based Schematic Analysis | Computer vision models for circuit board recognition | 6 weeks |
| Multi-User Collaboration | Role-based access control, shared investigations | 4 weeks |
| MITRE ATT&CK ICS Integration | Map findings to ATT&CK framework techniques | 3 weeks |
| Plugin Architecture | Third-party extensions for domain-specific parsers | 3 weeks |
| Hardware Acceleration | CUDA/ROCm optimisation for GPU-equipped laptops | 2 weeks |
| ICS Domain Fine-Tuning | Fine-tune base models on ICS vocabulary and concepts | 4 weeks |

**Estimated Phase 2 Budget:** £95,000 - £135,000 (16-24 weeks, 2 FTE)

---

## 17. How to Apply

This application is prepared for submission via the HMGCC Co-Creation website at https://co-creation.hmgcc.gov.uk/

For questions or clarification: Co-Creation@dstl.gov.uk / cocreation@hmgcc.gov.uk

---

*This document describes a working prototype built by Future Horizons Education to demonstrate how a Smart Personal Assistant for Security Researchers could function in practice, based on the project scope defined in HMGCC Co-Creation Challenge CH-2026-001. The prototype is available for live demonstration.*
