# REQUIREMENTS.md — Formal Requirements Traceability

## Source: HMGCC Co-Creation Challenge CH-2026-001

All requirements below are traced to the official HMGCC challenge document.
Status tracking: [ ] Not started | [~] In progress | [x] Complete

---

## Essential Requirements (MUST implement for MVP)

### ER-01: System Architecture Understanding
**Source:** HMGCC Challenge Form, Page 4, Essential Requirements, Bullet 1
**Description:** The tool must have the ability to understand system architecture of a selected machine. A non-exhaustive list of components to understand are the physical interface interactions, data interfaces and protocols.
**Acceptance Criteria:**
- Tool can ingest datasheets, schematics, and manuals describing a product
- Tool can extract and identify component names, types, interfaces, and protocols
- Tool can generate a structured representation of the system architecture
- Tool can answer questions about component relationships and interfaces
**Implementation:** core/architecture/extractor.py, core/architecture/mapper.py
**Sprint:** 4.1
**Status:** [x]

### ER-02: Response Validation & Anti-Hallucination
**Source:** HMGCC Challenge Form, Page 4, Essential Requirements, Bullet 2
**Description:** Have an ability to check and validate responses before publishing, to prevent erroneous information and hallucinations.
**Acceptance Criteria:**
- Every LLM response passes through a validation pipeline before display
- Factual claims in responses are cross-checked against retrieved source chunks
- Unsupported claims are flagged with "NOT FOUND IN SOURCES" warning
- Contradicted claims are flagged with "CONFLICTS WITH SOURCE" warning
- No raw LLM output reaches the user without validation
**Implementation:** core/validation/pipeline.py, core/validation/hallucination.py
**Sprint:** 2.3
**Status:** [x]

### ER-03: Multi-Modal Input Characterisation
**Source:** HMGCC Challenge Form, Page 4, Essential Requirements, Bullet 3
**Description:** Characterise from multimedia inputs, such as including manuals, schematics, datasheets, corporate databases, images, code, handwritten annotations.
**Acceptance Criteria:**
- Tool accepts and processes: PDF, PNG, JPG, TIFF, TXT, MD, HTML, C, H, PY, ASM, CSV, XLSX
- PDF parser extracts text, tables, and embedded images
- Image parser performs OCR on photographs, schematics, and handwritten annotations
- Code parser extracts function signatures, structs, constants, and comments
- Spreadsheet parser extracts tabular data into searchable text
- All parsed content is indexed and searchable
**Implementation:** core/ingest/parsers/
**Sprint:** 1.2
**Status:** [x]

### ER-04: Source Verification & Cross-Referencing
**Source:** HMGCC Challenge Form, Page 4, Essential Requirements, Bullet 4
**Description:** Verify information by listing sources and cross checking against high confidence data such as industry publications, academic research and manufacturer documentation.
**Acceptance Criteria:**
- Every answer includes a list of source documents used
- Sources are classified into quality tiers (Manufacturer > Academic > Trusted Forum > Unverified)
- When multiple sources discuss the same topic, agreements and disagreements are highlighted
- High-confidence data (Tier 1-2) is weighted more heavily than lower-tier sources
- Users can manually assign source quality tiers on import
**Implementation:** core/validation/source_tier.py, core/validation/cross_reference.py
**Sprint:** 2.3
**Status:** [x]

### ER-05: Confidence Scoring
**Source:** HMGCC Challenge Form, Page 4, Essential Requirements, Bullet 5
**Description:** Flag a confidence score and if more source data is required.
**Acceptance Criteria:**
- Every response includes a confidence score (0-100)
- Score is based on: number of corroborating sources, source quality tiers, consistency of information, coverage of the question
- Low confidence scores include a message suggesting what additional data might help
- Confidence explanation is human-readable (not just a number)
**Implementation:** core/validation/confidence.py
**Sprint:** 2.3
**Status:** [x]

### ER-06: Fully Offline Operation
**Source:** HMGCC Challenge Form, Page 4, Essential Requirements, Bullet 6
**Description:** The solution should be capable of operating on a laptop without an internet connection, allowing users to characterise complex systems and identify vulnerabilities in environments with limited or no connectivity.
**Acceptance Criteria:**
- All features function with network adapter disabled
- LLM inference runs locally via Ollama
- Embedding generation runs locally
- Vector database is embedded (ChromaDB, no server)
- No external API calls, telemetry, or cloud dependencies
- Zero network traffic during normal operation (verified by monitoring)
- Installation possible from offline media (USB/local package)
**Implementation:** Entire architecture; verified in Sprint 5.1
**Sprint:** All (verified 5.1)
**Status:** [x]

### ER-07: Intelligent Search & Chat Interface
**Source:** HMGCC Challenge Form, Page 4, Essential Requirements, Bullet 7
**Description:** Provide an easy to search and intelligent function to query the dataset in a chat-like manner.
**Acceptance Criteria:**
- Chat-like interface where users type natural language questions
- Responses are conversational, well-structured, and cite sources
- Hybrid search (vector + keyword) ensures both conceptual and exact-match queries work
- Results are relevant to the indexed document library
- Interface supports markdown rendering, code highlighting, and inline citations
**Implementation:** core/rag/engine.py, frontend/src/components/chat/
**Sprint:** 2.1 (backend), 3.2 (frontend)
**Status:** [x]

### ER-08: Conversational Memory
**Source:** HMGCC Challenge Form, Page 4, Essential Requirements, Bullet 8
**Description:** Keep a memory of queries so conversations can be continued over several weeks without repetition of prompts.
**Acceptance Criteria:**
- Conversations persist in SQLite across application restarts
- Resuming a conversation after days/weeks reconstructs context automatically
- Conversation summary is maintained and updated incrementally
- Key findings can be pinned as persistent facts
- Multiple concurrent conversation threads supported per project
- User does not need to repeat previously established context
**Implementation:** core/conversation/manager.py, core/conversation/summariser.py, core/conversation/memory.py
**Sprint:** 2.2
**Status:** [x]

---

## Desirable Requirements (SHOULD implement if time permits)

### DR-01: User Profiling & Adaptive Behaviour
**Source:** HMGCC Challenge Form, Page 4, Desirable Requirements, Bullet 1
**Description:** Build a profile of the user and adapt to their needs, for example to present information in preferred formats and even proactively provide information that is frequently requested.
**Acceptance Criteria:**
- Tool tracks query patterns, frequently accessed topics, and preferred detail level
- Responses adapt to learned preferences (concise vs detailed, tables vs prose)
- Proactive notifications when new documents relate to current investigation topics
- User can view and edit their learned profile
**Implementation:** core/profile/tracker.py, core/profile/adapter.py
**Sprint:** 4.3
**Status:** [x]

### DR-02: Non-English Data Support
**Source:** HMGCC Challenge Form, Page 4, Desirable Requirements, Bullet 2
**Description:** Ability to translate and index non-English data sources (e.g. datasheets and forum posts).
**Acceptance Criteria:**
- Tool detects non-English content during ingestion
- Non-English text is translated to English for indexing (using local translation model)
- Original language text is preserved alongside translation
- Search works across translated content
**Implementation:** core/ingest/translator.py
**Sprint:** 4.3 (stretch goal)
**Status:** [x]

### DR-03: Cultural Bias Mitigation
**Source:** HMGCC Challenge Form, Page 4, Desirable Requirements, Bullet 3
**Description:** Recognise and mitigate cultural biases to ensure a nuanced understanding.
**Acceptance Criteria:**
- System prompt instructs LLM to present information neutrally
- When sources from different regions/cultures conflict, both perspectives are presented
- No single cultural perspective is automatically privileged over others
**Implementation:** Prompt engineering in core/rag/context_builder.py
**Sprint:** 4.3
**Status:** [x]

### DR-04: Offline Update Mechanism
**Source:** HMGCC Challenge Form, Page 4, Desirable Requirements, Bullet 4
**Description:** Ensure the software tool remains up-to-date when offline. Consider in a future iteration how the solution may incorporate a mechanism for periodic updates of the core tool and its indexing/search algorithms.
**Acceptance Criteria:**
- Data export/import capability for migration between versions
- Model swap capability (load new LLM model files from USB/local storage)
- Clear versioning of the tool, models, and index format
- Documentation of update procedures
**Implementation:** scripts/update.py, backend/api/v1/settings.py
**Sprint:** 5.2
**Status:** [x]

---

## Constraints

### C-01: No Internet Connection
**Source:** HMGCC Challenge Form, Page 4, Constraints
**Description:** The tool must work without an internet connection.
**Enforcement:** Architectural constraint applied globally. Verified by offline testing with network disabled.

---

## Explicitly Not Required

### NR-01: Autonomous Data Discovery
**Source:** HMGCC Challenge Form, Page 4, Not Required
**Description:** For this challenge, the system does not need to autonomously identify or search for source data (e.g. datasheets, schematics and forum posts). Test data will be provided.
**Implication:** No web scraping, no automated data collection, no crawlers. All data is user-imported.

---

## Non-Functional Requirements

### NFR-01: Performance
**Target:** Query response < 10 seconds on modern laptop without GPU; < 3 seconds with GPU
**Measurement:** Automated performance benchmarks in test suite

### NFR-02: Scalability
**Target:** Handle datasets of several thousand documents (PDFs, images, code files) per project
**Measurement:** Load test with 2000+ document dataset

### NFR-03: Security
**Target:** All data remains local. No telemetry. Suitable for OFFICIAL classification.
**Measurement:** Network traffic monitoring during full test run shows zero external calls

### NFR-04: Portability
**Target:** Runs on standard Windows 10/11 or Linux laptop. No specialised hardware required.
**Measurement:** Successful installation and operation on clean Windows and Linux VMs

### NFR-05: Usability
**Target:** Intuitive chat interface. Drag-and-drop document import. No training required for basic use.
**Measurement:** User can complete core workflow (import → query → get answer) within 5 minutes of first launch

### NFR-06: Extensibility
**Target:** Architecture supports new document parsers, new LLM models, and updated indexing algorithms
**Measurement:** Adding a new parser requires only a new class implementing BaseParser

### NFR-07: Data Integrity
**Target:** No data loss or corruption. Full provenance metadata maintained for all sources.
**Measurement:** All documents traceable from answer citation back to original source file and page

---

## Requirements Traceability Matrix

| Requirement | Sprint(s) | Module(s) | Test(s) | Status |
|-------------|-----------|-----------|---------|--------|
| ER-01 | 4.1 | core/architecture/ | tests/test_architecture/ | [x] |
| ER-02 | 2.3 | core/validation/ | tests/test_validation/ | [x] |
| ER-03 | 1.2 | core/ingest/parsers/ | tests/test_ingest/ | [x] |
| ER-04 | 2.3 | core/validation/ | tests/test_validation/ | [x] |
| ER-05 | 2.3 | core/validation/confidence.py | tests/test_validation/ | [x] |
| ER-06 | All | All | tests/integration/test_offline.py | [x] |
| ER-07 | 2.1, 3.2 | core/rag/, frontend/chat/ | tests/test_rag/ | [x] |
| ER-08 | 2.2 | core/conversation/ | tests/test_conversation/ | [x] |
| DR-01 | 4.3 | core/profile/ | tests/test_profile/ | [x] |
| DR-02 | 4.3 | core/ingest/translator.py | tests/test_ingest/ | [x] |
| DR-03 | 4.3 | core/rag/context_builder.py | tests/test_rag/ | [x] |
| DR-04 | 5.2 | scripts/, backend/settings | tests/integration/ | [x] |
| NFR-01 | 5.1 | — | tests/benchmarks/ | [x] |
| NFR-02 | 5.1 | — | tests/benchmarks/ | [x] |
| NFR-03 | 5.1 | — | tests/integration/test_offline.py | [x] |
| NFR-04 | 5.2 | — | Manual test on clean VMs | [x] |
| NFR-05 | 3.1-3.3 | frontend/ | Manual UX testing | [x] |
| NFR-06 | 1.2 | core/ingest/parsers/base.py | Architectural review | [x] |
| NFR-07 | 1.2, 2.1 | core/ingest/, core/rag/ | tests/test_ingest/, tests/test_rag/ | [x] |

---

## Evaluation Alignment

The HMGCC evaluation scores proposals 1-5 across four criteria. This section maps how our implementation addresses each:

### Feasibility
- Technical credibility: proven open-source stack (Ollama, ChromaDB, FastAPI, Tauri)
- TRL 6 achievable: offline RAG is well-established pattern; all components are mature
- Team skills: AI/ML engineering, full-stack development, security domain expertise
- Risks identified: LLM quality offline (mitigated by model selection), OCR accuracy (mitigated by multi-strategy parsing)

### Desirability
- All 8 essential requirements addressed (ER-01 through ER-08)
- 4 desirable requirements addressed (DR-01 through DR-04)
- Goes beyond basic RAG: hybrid search, confidence scoring, hallucination detection, conversational memory, user profiling
- Dual-use potential: applicable to any technical research domain, not just security

### Viability
- Exploitation route: tool applicable across defence supply chain, critical infrastructure assessment, and commercial product security audit
- Commercial potential: SaaS version for non-classified use; licensing to allied nations; extension to other technical research domains
- Post-project plan: Phase 2 funding for autonomous data collection, ML-based schematic analysis, multi-user collaboration

### Budget
- £60,000 budget covers 12-week development with 1-2 FTE developers
- Open-source stack minimises licensing costs
- Offshore/AI-assisted development maximises output per pound
