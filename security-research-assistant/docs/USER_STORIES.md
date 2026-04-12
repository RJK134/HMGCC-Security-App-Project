# USER_STORIES.md — User Stories by Epic with Implementation Mapping

## Source: HMGCC Co-Creation Challenge CH-2026-001, Section 5

Each user story is mapped to the requirement(s) it satisfies, the sprint(s) where it is
implemented, and the specific module(s) responsible. Use this document as a checklist
during each sprint to ensure all relevant stories are addressed.

Status: [ ] Not started | [~] In progress | [x] Complete

---

## Epic 1: Data Ingestion & Indexing

**Sprint(s):** 1.2 (backend pipeline), 3.3 (frontend drag-and-drop)
**Primary modules:** `core/ingest/`, `backend/api/v1/documents.py`, `frontend/src/components/library/`

### US-1.1: Drag-and-Drop Document Import
> As a security researcher, I want to drag and drop technical documents (PDFs, manuals, schematics) into the tool so that they are automatically indexed and searchable.

| Field | Value |
|-------|-------|
| Requirements | ER-03, ER-07, NFR-05 |
| Sprint | 1.2 (backend), 3.3 (frontend) |
| Backend | `core/ingest/pipeline.py`, `core/ingest/detector.py`, `backend/api/v1/documents.py` |
| Frontend | `frontend/src/components/library/DropZone.tsx`, `frontend/src/components/library/ImportProgress.tsx` |
| Tests | `tests/test_ingest/test_pipeline.py` |
| Acceptance | User drops PDF/manual/schematic → file parsed, chunked, embedded, stored in ChromaDB → searchable via query |
| Status | [ ] |

### US-1.2: Image Import with OCR
> As a security researcher, I want to import images of circuit boards, wiring diagrams, and handwritten annotations so that the tool can extract and characterise the information within them.

| Field | Value |
|-------|-------|
| Requirements | ER-03 |
| Sprint | 1.2 |
| Backend | `core/ingest/parsers/image_parser.py` (Tesseract OCR + Pillow) |
| Tests | `tests/test_ingest/test_image_parser.py` |
| Acceptance | Upload PNG/JPG/TIFF of circuit board or handwritten notes → OCR extracts text → text indexed and searchable |
| Status | [ ] |

### US-1.3: Datasheets, Code, and Binary Import
> As a security researcher, I want to import datasheets, source code, and binary files so that the tool can understand the software and hardware components of a product.

| Field | Value |
|-------|-------|
| Requirements | ER-03, ER-01 |
| Sprint | 1.2 |
| Backend | `core/ingest/parsers/pdf_parser.py` (datasheets), `core/ingest/parsers/code_parser.py` (tree-sitter) |
| Tests | `tests/test_ingest/test_pdf_parser.py`, `tests/test_ingest/test_code_parser.py` |
| Acceptance | Upload datasheet PDF → tabular data extracted. Upload .c/.py/.asm → functions, structs, constants extracted. All indexed. |
| Status | [ ] |

### US-1.4: Structured and Unstructured Data Unified
> As a security researcher, I want the tool to process and index structured data (databases, spreadsheets) alongside unstructured data (forum posts, PDFs) into a unified searchable library.

| Field | Value |
|-------|-------|
| Requirements | ER-03 |
| Sprint | 1.2 |
| Backend | `core/ingest/parsers/spreadsheet_parser.py`, `core/ingest/parsers/text_parser.py`, `core/ingest/chunker.py` |
| Tests | `tests/test_ingest/test_spreadsheet_parser.py`, `tests/test_ingest/test_text_parser.py` |
| Acceptance | Upload CSV/XLSX and forum post HTML → all content chunked, embedded, stored in same ChromaDB collection → single query searches across all types |
| Status | [ ] |

### US-1.5: Organise by Project
> As a security researcher, I want to organise imported data by product, component, or investigation so I can manage multiple concurrent research projects.

| Field | Value |
|-------|-------|
| Requirements | NFR-02 |
| Sprint | 1.1 (data model), 3.1 (frontend) |
| Backend | `core/database/repositories/project_repo.py`, `backend/api/v1/projects.py`, `core/vector_store/chroma_client.py` (per-project collections) |
| Frontend | `frontend/src/components/projects/ProjectList.tsx`, `frontend/src/components/projects/ProjectForm.tsx` |
| Tests | `tests/test_ingest/test_project_isolation.py` |
| Acceptance | Create Project A and Project B → import different docs to each → queries in Project A only return Project A documents |
| Status | [ ] |

---

## Epic 2: Search & Query

**Sprint(s):** 2.1 (RAG engine), 2.3 (validation), 3.2 (chat UI)
**Primary modules:** `core/rag/`, `core/validation/`, `frontend/src/components/chat/`

### US-2.1: Natural-Language Questions
> As a security researcher, I want to ask natural-language questions about my indexed data and receive conversational, well-grounded answers.

| Field | Value |
|-------|-------|
| Requirements | ER-07 |
| Sprint | 2.1 (backend), 3.2 (frontend) |
| Backend | `core/rag/engine.py`, `core/rag/vector_search.py`, `core/rag/keyword_search.py`, `core/rag/fusion.py`, `core/rag/llm_client.py` |
| Frontend | `frontend/src/components/chat/ChatWindow.tsx`, `frontend/src/components/chat/InputArea.tsx` |
| Tests | `tests/test_rag/test_engine.py`, `tests/test_rag/test_fusion.py` |
| Acceptance | Type "What interfaces does the main processor use?" → receive grounded answer citing ingested datasheets |
| Status | [ ] |

### US-2.2: Source Citations
> As a security researcher, I want every answer to cite its sources so I can verify the information and assess its trustworthiness.

| Field | Value |
|-------|-------|
| Requirements | ER-04, NFR-07 |
| Sprint | 2.1 (response parsing), 3.2 (citation UI) |
| Backend | `core/rag/response_parser.py`, `core/rag/context_builder.py` (prompt instructs citation) |
| Frontend | `frontend/src/components/chat/CitationBadge.tsx`, `frontend/src/components/chat/MessageBubble.tsx` |
| Tests | `tests/test_rag/test_response_parser.py` |
| Acceptance | Every answer includes [Source: filename, page X] references → clicking citation in UI shows source document |
| Status | [ ] |

### US-2.3: Confidence Scores
> As a security researcher, I want the tool to flag confidence scores on its answers so I know when more source data may be needed.

| Field | Value |
|-------|-------|
| Requirements | ER-05 |
| Sprint | 2.3 (scoring), 3.2 (confidence UI) |
| Backend | `core/validation/confidence.py` |
| Frontend | `frontend/src/components/chat/ConfidenceBar.tsx` |
| Tests | `tests/test_validation/test_confidence.py` |
| Acceptance | Well-sourced answer shows high confidence (70-100). Sparse-source answer shows low confidence (0-40) with suggestion for additional data. |
| Status | [ ] |

### US-2.4: Follow-Up Questions with Context
> As a security researcher, I want to ask follow-up questions that build on prior conversation context so I can explore topics interactively.

| Field | Value |
|-------|-------|
| Requirements | ER-08 |
| Sprint | 2.2 |
| Backend | `core/conversation/manager.py`, `core/conversation/summariser.py`, `core/rag/context_builder.py` |
| Tests | `tests/test_conversation/test_context.py` |
| Acceptance | Ask "What processor does this use?" then "What are its GPIO pins?" → second answer correctly refers to the processor from the first answer |
| Status | [ ] |

### US-2.5: Alternative Theories
> As a security researcher, I want the tool to present alternative theories or interpretations when information is ambiguous.

| Field | Value |
|-------|-------|
| Requirements | ER-02, ER-04 |
| Sprint | 2.1 (prompt engineering), 2.3 (validation), 3.2 (UI panel) |
| Backend | `core/rag/context_builder.py` (prompt instructs alternatives), `core/validation/cross_reference.py` |
| Frontend | `frontend/src/components/chat/AlternativePanel.tsx` |
| Tests | `tests/test_rag/test_alternatives.py` |
| Acceptance | When sources disagree on a component specification → response presents both interpretations with source attribution |
| Status | [ ] |

---

## Epic 3: Summary & Report Generation

**Sprint(s):** 4.1 (architecture), 4.2 (reports)
**Primary modules:** `core/architecture/`, `core/reports/`, `backend/api/v1/reports.py`

### US-3.1: Technical Summaries
> As a security researcher, I want the tool to generate a clear technical summary of a product and its individual components based on my indexed data.

| Field | Value |
|-------|-------|
| Requirements | ER-01 |
| Sprint | 4.2 |
| Backend | `core/reports/generator.py`, `core/reports/templates.py` (Product Overview template) |
| Tests | `tests/test_reports/test_generator.py` |
| Acceptance | Request summary for project → receive structured overview of product, its components, key specifications, and identified interfaces |
| Status | [ ] |

### US-3.2: Structured Architecture Reports
> As a security researcher, I want to generate structured reports showing the system architecture, component relationships, interfaces, and protocols of a product.

| Field | Value |
|-------|-------|
| Requirements | ER-01 |
| Sprint | 4.1 (extraction), 4.2 (report) |
| Backend | `core/architecture/extractor.py`, `core/architecture/mapper.py`, `core/reports/templates.py` (Architecture Report template) |
| Frontend | `frontend/src/components/architecture/ComponentMap.tsx` |
| Tests | `tests/test_architecture/test_extractor.py`, `tests/test_architecture/test_mapper.py` |
| Acceptance | Trigger architecture extraction → component graph built → report shows components, interfaces, protocols, communication pathways |
| Status | [ ] |

### US-3.3: Export Reports
> As a security researcher, I want to export summaries and reports for use in my vulnerability assessment workflow.

| Field | Value |
|-------|-------|
| Requirements | ER-01 |
| Sprint | 4.2 |
| Backend | `core/reports/exporter.py` (PDF via reportlab, Markdown, JSON), `backend/api/v1/reports.py` |
| Frontend | `frontend/src/components/reports/ReportBuilder.tsx` |
| Tests | `tests/test_reports/test_exporter.py` |
| Acceptance | Generate report → export as PDF, Markdown, or JSON → file downloads correctly with all citations and confidence scores included |
| Status | [ ] |

---

## Epic 4: Validation & Trust

**Sprint(s):** 2.3
**Primary modules:** `core/validation/`

### US-4.1: Cross-Reference Against High-Confidence Sources
> As a security researcher, I want the tool to cross-reference information against high-confidence sources (manufacturer documentation, academic research, industry publications).

| Field | Value |
|-------|-------|
| Requirements | ER-04 |
| Sprint | 2.3 |
| Backend | `core/validation/cross_reference.py`, `core/validation/source_tier.py` |
| Tests | `tests/test_validation/test_cross_reference.py` |
| Acceptance | Answer uses Tier 1 and Tier 4 sources → cross-reference highlights where they agree and disagree → Tier 1 weighted more heavily |
| Status | [ ] |

### US-4.2: Validate Before Display, Flag Hallucinations
> As a security researcher, I want the tool to validate responses before displaying them and flag any potential hallucinations or low-confidence information.

| Field | Value |
|-------|-------|
| Requirements | ER-02 |
| Sprint | 2.3 |
| Backend | `core/validation/pipeline.py`, `core/validation/hallucination.py` |
| Tests | `tests/test_validation/test_hallucination.py` |
| Acceptance | LLM fabricates a claim not in sources → validation flags it with "NOT FOUND IN SOURCES" → user sees warning before the claim |
| Status | [ ] |

### US-4.3: Distinguish Data Origins
> As a security researcher, I want the tool to distinguish between vendor-provided data, community-sourced data, and inferred information.

| Field | Value |
|-------|-------|
| Requirements | ER-04, ER-05 |
| Sprint | 2.3, 1.2 (tier assignment on import) |
| Backend | `core/validation/source_tier.py`, `core/ingest/pipeline.py` (tier metadata), `backend/api/v1/documents.py` (PATCH tier) |
| Tests | `tests/test_validation/test_source_tier.py` |
| Acceptance | Answer cites 3 sources → each citation labelled with origin type (Manufacturer / Community / Inferred) → user can filter by origin |
| Status | [ ] |

---

## Epic 5: Conversational Memory & Personalisation

**Sprint(s):** 2.2 (memory), 4.3 (profiling)
**Primary modules:** `core/conversation/`, `core/profile/`

### US-5.1: Resume After Weeks
> As a security researcher, I want to resume conversations weeks later without re-explaining context, so I can work on long-running investigations.

| Field | Value |
|-------|-------|
| Requirements | ER-08 |
| Sprint | 2.2 |
| Backend | `core/conversation/manager.py` (session resume), `core/conversation/summariser.py` (context compression), `core/conversation/memory.py` (pinned facts) |
| Tests | `tests/test_conversation/test_resume.py` |
| Acceptance | Have conversation → close app → reopen weeks later → resume conversation → assistant recalls previous context without user repeating it |
| Status | [ ] |

### US-5.2: Learn Preferences and Surface Relevant Data
> As a security researcher, I want the tool to learn my preferences for information presentation and proactively surface relevant data.

| Field | Value |
|-------|-------|
| Requirements | DR-01 |
| Sprint | 4.3 |
| Backend | `core/profile/tracker.py`, `core/profile/adapter.py` |
| Tests | `tests/test_profile/test_tracker.py`, `tests/test_profile/test_adapter.py` |
| Acceptance | After 20+ queries, tool adapts response style. When new documents ingested that relate to active investigation, notification surfaces. |
| Status | [ ] |

### US-5.3: Multiple Investigation Threads
> As a security researcher, I want to maintain multiple investigation threads with separate conversation histories.

| Field | Value |
|-------|-------|
| Requirements | ER-08 |
| Sprint | 2.2 (backend), 3.2 (frontend) |
| Backend | `core/conversation/manager.py`, `core/database/repositories/conversation_repo.py`, `backend/api/v1/conversations.py` |
| Frontend | `frontend/src/components/chat/ChatWindow.tsx` (conversation selector) |
| Tests | `tests/test_conversation/test_multi_thread.py` |
| Acceptance | Create Thread A and Thread B in same project → each has independent history → switching threads loads correct context |
| Status | [ ] |

---

## Epic 6: Offline Operation

**Sprint(s):** All (architectural constraint), 5.1 (verification), 5.2 (packaging)
**Primary modules:** Entire architecture

### US-6.1: Fully Local Operation
> As a security researcher, I want the entire tool (including LLM inference, vector search, and indexing) to run locally on a laptop with no internet dependency.

| Field | Value |
|-------|-------|
| Requirements | ER-06, C-01, NFR-03 |
| Sprint | All (enforced), 5.1 (verified) |
| Backend | All modules — Ollama (local LLM), ChromaDB (embedded), SQLite (local), sentence-transformers (local embeddings) |
| Tests | `tests/integration/test_offline.py` |
| Acceptance | Disable network adapter → run full workflow (import → query → report) → all features work → network monitor shows zero external calls |
| Status | [ ] |

### US-6.2: Simple Offline Installer
> As a security researcher, I want to install the tool via a simple offline deployment package.

| Field | Value |
|-------|-------|
| Requirements | ER-06, DR-04, NFR-04 |
| Sprint | 5.2 |
| Backend | Tauri NSIS installer (Windows), AppImage (Linux), bundled Ollama + default model |
| Tests | Manual installation test on clean Windows and Linux VMs |
| Acceptance | Copy installer to air-gapped machine → run installer → tool functional within 15 minutes → includes bundled LLM model |
| Status | [ ] |

---

## Sprint Cross-Reference: Which Stories to Check Per Sprint

Use this table during sprint reviews to verify all relevant stories are satisfied.

| Sprint | User Stories |
|--------|-------------|
| 1.1 | US-1.5 (data model for projects) |
| 1.2 | US-1.1, US-1.2, US-1.3, US-1.4, US-4.3 (tier on import) |
| 2.1 | US-2.1, US-2.2, US-2.5 (prompt engineering) |
| 2.2 | US-2.4, US-5.1, US-5.3 |
| 2.3 | US-2.3, US-2.5 (validation), US-4.1, US-4.2, US-4.3 |
| 3.1 | US-1.5 (project UI) |
| 3.2 | US-2.1, US-2.2, US-2.3, US-2.5, US-5.3 (frontend) |
| 3.3 | US-1.1 (drag-and-drop UI) |
| 4.1 | US-3.2 (architecture extraction) |
| 4.2 | US-3.1, US-3.2, US-3.3 |
| 4.3 | US-5.2 |
| 5.1 | US-6.1 (offline verification) |
| 5.2 | US-6.2 |
