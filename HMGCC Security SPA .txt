HMGCC Co-Creation Challenge: Smart Personal Assistant for Security Researchers
Complete Specification, Build Plan & Claude Code Implementation Guide

1. EXECUTIVE SUMMARY
Challenge ID: CH-2026-001
Issuer: HMGCC Co-Creation (partnership between HMGCC and Dstl — Defence Science and Technology Laboratory)
Budget: £60,000 (exc VAT)
Duration: 12 weeks
Target TRL: Technology Readiness Level 6 (System/subsystem model or prototype demonstration in a relevant environment)
Key Constraint: Must operate fully offline — no internet connection required
Competition Close: 7 May 2026
Target Kick-off: July 2026

2. PROBLEM STATEMENT
National security organisations procure complex industrial machinery that must be thoroughly checked for security vulnerabilities. Security researchers conduct detailed tear-downs of software, hardware, and data components. The bottleneck is the initial research phase — finding, indexing, and understanding vast amounts of open-source technical information (datasheets, schematics, technical forum posts, specifications) about complex industrial control systems at a micro-component level. This tool aims to use human-machine teaming to reduce that research burden.

3. CORE FUNCTIONAL REQUIREMENTS
3.1 Essential Requirements (MUST HAVE)
ER-01: System Architecture Understanding
The tool must understand the system architecture of a selected machine. It must handle physical interface interactions, data interfaces, and protocols. Components include filters, fuses, processors, memory sensors, and software across source code or binary for multiple processors and operating systems in the same product.
ER-02: Response Validation & Anti-Hallucination
Must check and validate responses before publishing to prevent erroneous information and hallucinations.
ER-03: Multi-Modal Input Characterisation
Must characterise from multimedia inputs including manuals, schematics, datasheets, corporate databases, images, code, and handwritten annotations.
ER-04: Source Verification & Cross-Referencing
Must verify information by listing sources and cross-checking against high-confidence data such as industry publications, academic research, and manufacturer documentation.
ER-05: Confidence Scoring
Must flag a confidence score and indicate if more source data is required.
ER-06: Fully Offline Operation
Must operate on a laptop without an internet connection, allowing users to characterise complex systems and identify vulnerabilities in environments with limited or no connectivity.
ER-07: Intelligent Search & Chat Interface
Must provide an easy-to-use search and intelligent function to query the dataset in a chat-like manner.
ER-08: Conversational Memory
Must keep a memory of queries so conversations can be continued over several weeks without repetition of prompts.
3.2 Desirable Requirements (SHOULD HAVE)
DR-01: User Profiling & Adaptive Behaviour
Build a profile of the user and adapt to their needs — present information in preferred formats and proactively provide frequently requested information.
DR-02: Non-English Data Support
Ability to translate and index non-English data sources (e.g., datasheets and forum posts).
DR-03: Cultural Bias Mitigation
Recognise and mitigate cultural biases to ensure nuanced understanding.
DR-04: Offline Update Mechanism
Ensure the tool remains up-to-date when offline. Consider a mechanism for periodic updates of the core tool and its indexing/search algorithms in a future iteration.
3.3 Constraints
C-01: The tool MUST work without an internet connection.
3.4 Not Required (Explicitly Out of Scope)
The system does not need to autonomously identify or search for source data (e.g., datasheets, schematics, forum posts). Test data will be provided by HMGCC.

4. DETAILED USE CASE (from Challenge Document)
Persona: "Alicia" — experienced security researcher focused on industrial control systems.
Scenario: Tasked to assess an industrial additive manufacturing machine used in a classified manufacturing facility without internet. She must understand and mitigate all vulnerabilities.
Workflow:

Begins with vendor manual (paper copy and PDF)
Uses wiring diagrams and schematics to investigate hardware architecture (interfaces, components, microprocessors)
Sources datasheets online for each component, finds photos of tear-downs
Pulls out all available vendor-supplied code
Consults online forums (some trusted, some new)
Builds a large library of information — drags and drops data into the tool
Needs intelligent search and summary capability across the library
Types natural-language queries, receives conversational responses backed by reliable sources
Builds follow-up question chains, receives well-grounded answers citing sources
Where answers are unclear, alternative theories are highlighted
The assistant learns and adapts to Alicia's behaviour over time


5. USER STORIES
Epic 1: Data Ingestion & Indexing
US-1.1 As a security researcher, I want to drag and drop technical documents (PDFs, manuals, schematics) into the tool so that they are automatically indexed and searchable.
US-1.2 As a security researcher, I want to import images of circuit boards, wiring diagrams, and handwritten annotations so that the tool can extract and characterise the information within them.
US-1.3 As a security researcher, I want to import datasheets, source code, and binary files so that the tool can understand the software and hardware components of a product.
US-1.4 As a security researcher, I want the tool to process and index structured data (databases, spreadsheets) alongside unstructured data (forum posts, PDFs) into a unified searchable library.
US-1.5 As a security researcher, I want to organise imported data by product, component, or investigation so I can manage multiple concurrent research projects.
Epic 2: Search & Query
US-2.1 As a security researcher, I want to ask natural-language questions about my indexed data and receive conversational, well-grounded answers.
US-2.2 As a security researcher, I want every answer to cite its sources so I can verify the information and assess its trustworthiness.
US-2.3 As a security researcher, I want the tool to flag confidence scores on its answers so I know when more source data may be needed.
US-2.4 As a security researcher, I want to ask follow-up questions that build on prior conversation context so I can explore topics interactively.
US-2.5 As a security researcher, I want the tool to present alternative theories or interpretations when information is ambiguous.
Epic 3: Summary & Report Generation
US-3.1 As a security researcher, I want the tool to generate a clear technical summary of a product and its individual components based on my indexed data.
US-3.2 As a security researcher, I want to generate structured reports showing the system architecture, component relationships, interfaces, and protocols of a product.
US-3.3 As a security researcher, I want to export summaries and reports for use in my vulnerability assessment workflow.
Epic 4: Validation & Trust
US-4.1 As a security researcher, I want the tool to cross-reference information against high-confidence sources (manufacturer documentation, academic research, industry publications).
US-4.2 As a security researcher, I want the tool to validate responses before displaying them and flag any potential hallucinations or low-confidence information.
US-4.3 As a security researcher, I want the tool to distinguish between vendor-provided data, community-sourced data, and inferred information.
Epic 5: Conversational Memory & Personalisation
US-5.1 As a security researcher, I want to resume conversations weeks later without re-explaining context, so I can work on long-running investigations.
US-5.2 As a security researcher, I want the tool to learn my preferences for information presentation and proactively surface relevant data.
US-5.3 As a security researcher, I want to maintain multiple investigation threads with separate conversation histories.
Epic 6: Offline Operation
US-6.1 As a security researcher, I want the entire tool (including LLM inference, vector search, and indexing) to run locally on a laptop with no internet dependency.
US-6.2 As a security researcher, I want to install the tool via a simple offline deployment package.

6. NON-FUNCTIONAL REQUIREMENTS
NFR-01 Performance: Responses to queries should return within a reasonable timeframe (target <10 seconds) on a modern laptop without GPU acceleration, or <3 seconds with GPU.
NFR-02 Scalability: Must handle datasets equivalent to several thousand documents (PDFs, datasheets, images, code files) for a single product investigation.
NFR-03 Security: All data must remain local. No telemetry, no network calls. Suitable for OFFICIAL classification environments.
NFR-04 Portability: Must run on a standard laptop (Windows or Linux). No specialised hardware required beyond what a security researcher would typically have.
NFR-05 Usability: Chat-like interface that is intuitive without training. Drag-and-drop data ingestion.
NFR-06 Extensibility: Architecture should support future addition of new document parsers, new LLM models, and updated indexing algorithms.
NFR-07 Data Integrity: Must not corrupt or lose ingested data. Must maintain provenance metadata for all sources.

7. TECHNOLOGY ARCHITECTURE (MVP)
7.1 Proposed Stack
LayerTechnologyRationaleLocal LLMOllama + Mistral/Llama 3 (or similar quantized model)Runs fully offline, supports conversational queries, strong reasoningEmbedding Modelall-MiniLM-L6-v2 or nomic-embed-text (via Ollama)Offline sentence embeddings for RAGVector DatabaseChromaDB or LanceDBLightweight, embedded, no server needed, Python-nativeDocument ProcessingLangChain / LlamaIndex document loadersPDF, DOCX, images, code parsingOCR/Image ProcessingTesseract OCR + PIL/OpenCVHandwritten annotations, schematics, circuit board imagesCode AnalysisTree-sitter + custom parsersSource code and binary analysis characterisationFrontendElectron or Tauri + React/SvelteDesktop app with drag-and-drop, chat UIBackendPython FastAPIOrchestration, RAG pipeline, LLM interactionConversation StoreSQLitePersistent conversation history, user profilesSearchHybrid: vector similarity + BM25 keyword searchBest of both worlds for retrieval
7.2 Architecture Diagram (Conceptual)
┌──────────────────────────────────────────────────────┐
│                    DESKTOP APP (Electron/Tauri)       │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │  Chat UI     │  │ Data Import  │  │  Reports    │ │
│  │  (React)     │  │ Drag & Drop  │  │  Export     │ │
│  └──────┬──────┘  └──────┬───────┘  └──────┬──────┘ │
└─────────┼────────────────┼─────────────────┼─────────┘
          │                │                 │
┌─────────▼────────────────▼─────────────────▼─────────┐
│              PYTHON BACKEND (FastAPI)                  │
│  ┌────────────┐ ┌──────────────┐ ┌────────────────┐  │
│  │ RAG Engine │ │  Doc Parser  │ │ Summary Gen    │  │
│  │ (LlamaIdx) │ │  Pipeline    │ │ & Validation   │  │
│  └─────┬──────┘ └──────┬───────┘ └───────┬────────┘  │
│        │               │                 │            │
│  ┌─────▼───────────────▼─────────────────▼────────┐  │
│  │            Orchestration Layer                   │  │
│  │   - Query routing  - Confidence scoring         │  │
│  │   - Source tracking - Hallucination detection    │  │
│  └─────┬──────────────────────────────────┬───────┘  │
└────────┼──────────────────────────────────┼──────────┘
         │                                  │
┌────────▼──────────┐           ┌───────────▼──────────┐
│   LOCAL LLM       │           │   DATA STORES        │
│   (Ollama)        │           │  ┌────────────────┐  │
│  - Mistral/Llama  │           │  │ ChromaDB       │  │
│  - Embeddings     │           │  │ (Vectors)      │  │
│                   │           │  ├────────────────┤  │
│                   │           │  │ SQLite         │  │
│                   │           │  │ (Conversations │  │
│                   │           │  │  User Profiles │  │
│                   │           │  │  Metadata)     │  │
│                   │           │  └────────────────┘  │
└───────────────────┘           └──────────────────────┘

8. EVALUATION CRITERIA (from HMGCC)
The proposal will be scored 1–5 across these dimensions:
Feasibility — Technical credibility of the MVP. Is it technically possible? Key technical risks identified? Likelihood of reaching TRL 6? Team credibility (expertise, experience, prior similar delivery).
Desirability — Does the proposal achieve all essential requirements? How many desirable requirements? Benefit for government and dual-use. Ambition of the solution (incremental step vs. significant leap). Uniqueness.
Viability — Exploitation route described? Commercial thinking beyond the project? Rough costings for future work? Value for money with justified cost breakdown.
Budget — Are project finances within the £60,000 competition scope?

9. SKILLS & ROLES REQUIRED
9.1 Core Team Roles for Claude Code Build
Role 1: AI/ML Engineer (Lead)
Responsible for LLM integration (Ollama), RAG pipeline design, embedding model selection and tuning, hallucination detection, confidence scoring, and conversational memory. This is the primary Claude Code operator role.
Role 2: Full-Stack Developer
Responsible for the desktop application (Electron/Tauri), React/Svelte chat UI, drag-and-drop ingestion interface, report export functionality, and backend API (FastAPI).
Role 3: Document Processing / NLP Specialist
Responsible for multi-modal document parsing pipeline (PDF, images, schematics, code, handwritten annotations), OCR integration, and structured/unstructured data indexing.
Role 4: Security / Domain Consultant
Provides domain expertise on ICS (Industrial Control Systems), hardware tear-down workflows, vulnerability research methodologies, and validates that the tool meets the needs of security researchers.
Role 5: QA / Test Engineer
Responsible for validation testing with representative datasets, offline deployment verification, performance benchmarking, and user acceptance testing.
9.2 Key Technical Skills
AI/ML: local LLM deployment, RAG architectures, prompt engineering, embedding models, vector databases. Backend: Python, FastAPI, LangChain/LlamaIndex, SQLite. Frontend: TypeScript, React or Svelte, Electron or Tauri. Document Processing: OCR (Tesseract), PDF parsing, image analysis, code parsing (tree-sitter). DevOps: offline packaging, installer creation, cross-platform deployment. Domain: ICS security, hardware vulnerability research, OSINT methodologies.

10. DETAILED CLAUDE CODE BUILD PLAN
Phase 1: Foundation (Weeks 1–2)
Sprint 1.1: Project Scaffolding & Core Infrastructure
Claude Code Prompt:
Create a Python project called "security-research-assistant" with the following structure:
- /backend (FastAPI application)
- /frontend (React + TypeScript desktop app shell using Tauri)
- /core (core library: RAG engine, document processing, LLM interface)
- /data (local data storage directory)
- /tests

Set up:
1. Python backend with FastAPI, uvicorn, pydantic
2. Ollama integration layer that detects available local models and can run inference
3. ChromaDB vector store initialization with collection management
4. SQLite database schema for: conversations, messages, documents, user_profiles, sources
5. Basic health check API endpoints
6. Configuration management (YAML-based, no hardcoded paths)
7. Logging infrastructure

Ensure everything works fully offline. No external API calls. All dependencies must be vendorable.
Verification Steps:

Run pytest — all infrastructure tests pass
Start FastAPI server — health endpoint returns 200
Ollama connection test (with a small test model)
ChromaDB creates collections successfully
SQLite tables created with correct schema

Sprint 1.2: Document Ingestion Pipeline
Claude Code Prompt:
Build a multi-modal document ingestion pipeline in /core/ingest/ that can:

1. Accept files via API endpoint (POST /api/v1/documents/upload)
2. Detect file type and route to appropriate parser:
   - PDF: Extract text using PyMuPDF, extract images, handle multi-column layouts
   - Images (PNG, JPG, TIFF): OCR using Tesseract, extract text from schematics
   - Code files (.c, .h, .py, .asm, etc.): Parse using tree-sitter, extract functions, structs, comments
   - Datasheets (PDF): Special handling for tabular data extraction
   - Plain text, markdown, HTML: Standard text extraction
3. Chunk documents intelligently:
   - Use semantic chunking (not fixed-size) with overlap
   - Preserve document structure (headings, sections, tables)
   - Maintain metadata: source file, page number, chunk position, document type
4. Generate embeddings using a local embedding model (via Ollama or sentence-transformers)
5. Store in ChromaDB with full metadata
6. Store document metadata and processing status in SQLite
7. Support batch import (directory of files)
8. Return processing status and any errors/warnings

Include proper error handling, progress tracking, and logging.
Verification Steps:

Upload a sample PDF — text extracted and chunked correctly
Upload an image with text — OCR extracts readable content
Upload a code file — functions and structures identified
Check ChromaDB — embeddings stored with correct metadata
Check SQLite — document records created
Batch import test with 20+ mixed files

Phase 2: Core Intelligence (Weeks 3–5)
Sprint 2.1: RAG Engine & Query Pipeline
Claude Code Prompt:
Build the RAG (Retrieval-Augmented Generation) query engine in /core/rag/:

1. Hybrid search combining:
   - Vector similarity search (ChromaDB) for semantic matching
   - BM25 keyword search for exact term matching
   - Reciprocal Rank Fusion to merge results
2. Query processing:
   - Analyse user query to determine intent (factual, exploratory, comparative)
   - Expand query with synonyms relevant to ICS/security domain
   - Route to appropriate retrieval strategy
3. Context assembly:
   - Retrieve top-k relevant chunks (configurable, default 10)
   - Re-rank using cross-encoder or LLM-based reranking
   - Assemble context window respecting LLM token limits
   - Include source metadata in context
4. Response generation:
   - Send assembled prompt to local LLM via Ollama
   - System prompt instructs the model to: cite sources, flag uncertainty, present alternatives when ambiguous
   - Parse response to extract citations and map to source documents
5. Post-processing:
   - Confidence score calculation based on: number of corroborating sources, source quality tier, consistency of information
   - Hallucination detection: cross-reference claims against retrieved chunks
   - Source attribution: list all sources used with document name, page, and relevance score
6. API endpoint: POST /api/v1/query with conversation_id support

Include comprehensive unit tests for each component.
Verification Steps:

Query against ingested test data returns relevant, cited answers
Confidence scores vary appropriately (high for well-sourced, low for sparse)
Hallucination detector catches fabricated claims (test with adversarial prompts)
Sources listed match actual retrieved documents
Hybrid search returns better results than vector-only or keyword-only

Sprint 2.2: Conversational Memory & Context Management
Claude Code Prompt:
Build conversation management in /core/conversation/:

1. Conversation CRUD:
   - Create new conversations with title, associated project/product
   - Store messages (user + assistant) with timestamps in SQLite
   - Retrieve conversation history with pagination
   - Support multiple concurrent conversation threads
2. Context window management:
   - On each new query, load relevant conversation history
   - Summarise older messages to fit within LLM context window
   - Maintain a "conversation summary" that updates after each exchange
3. Long-term memory:
   - Store key facts/findings extracted from conversations
   - Allow user to pin important discoveries
   - When resuming after days/weeks, reconstruct context from:
     a) Conversation summary
     b) Pinned facts
     c) Recent message history
4. API endpoints:
   - GET /api/v1/conversations (list all)
   - GET /api/v1/conversations/{id} (get with messages)
   - POST /api/v1/conversations (create new)
   - DELETE /api/v1/conversations/{id}
   - POST /api/v1/conversations/{id}/pin (pin a finding)
Verification Steps:

Create conversation, send 5 messages, retrieve correctly
Resume conversation after simulated gap — context is reconstructed
Pinned facts appear in subsequent query context
Multiple conversations remain isolated
Old conversation summary is accurate

Sprint 2.3: Validation & Confidence Engine
Claude Code Prompt:
Build the validation and confidence scoring engine in /core/validation/:

1. Source quality classification:
   - Tier 1 (highest): Manufacturer documentation, official datasheets
   - Tier 2: Academic papers, industry standards (IEEE, IEC)
   - Tier 3: Trusted technical forums, known expert blogs
   - Tier 4: General forum posts, unverified sources
   - Allow user to manually classify sources on import
2. Confidence scoring algorithm:
   - Base score from source tier weighting
   - Boost for corroboration across multiple independent sources
   - Penalty for contradictory information
   - Penalty for single-source claims
   - Output: score 0-100 with explanation
3. Hallucination detection:
   - Compare each claim in LLM response against retrieved chunks
   - Flag claims that don't have supporting evidence in retrieved context
   - Flag claims that contradict retrieved evidence
   - Present flagged items to user with explanation
4. Cross-referencing:
   - When multiple sources discuss the same component/topic, compare claims
   - Highlight agreements and disagreements
   - Present a synthesised view with provenance
5. Response validation pipeline:
   - All LLM responses pass through validation before display
   - Validated response includes: answer text, confidence score, source list, flagged items, alternative interpretations
Verification Steps:

Source classification correctly tiers different document types
Confidence scores correlate with ground truth (test with known-good and known-bad data)
Hallucination detection catches inserted false claims
Cross-referencing identifies contradictions between sources
Validated responses include all required metadata

Phase 3: User Interface (Weeks 5–7)
Sprint 3.1: Desktop Application Shell
Claude Code Prompt:
Build the desktop application using Tauri + React + TypeScript:

1. Application shell:
   - Native window with menu bar
   - Sidebar navigation: Projects, Chat, Library, Settings
   - Main content area with responsive layout
   - System tray integration for background operation
2. Project management view:
   - Create/edit/delete investigation projects
   - Each project has its own document library and conversations
3. Settings panel:
   - LLM model selection (list available Ollama models)
   - Chunk size and retrieval parameters
   - Source quality tier configuration
   - User profile preferences
4. Offline installer:
   - Tauri builds as standalone executable
   - Bundle Ollama or detect existing installation
   - First-run setup wizard
Sprint 3.2: Chat Interface
Claude Code Prompt:
Build the chat interface component in React:

1. Chat window:
   - Message bubbles for user and assistant
   - Markdown rendering in assistant responses
   - Code syntax highlighting for technical content
   - Inline source citations (clickable to view source document)
   - Confidence score badge on each response
   - Flagged items shown as expandable warnings
   - Alternative theories section when applicable
2. Input area:
   - Multi-line text input with send button
   - Keyboard shortcuts (Enter to send, Shift+Enter for newline)
   - Conversation selector (dropdown to switch threads)
   - "New conversation" button
3. Conversation sidebar:
   - List of conversations grouped by project
   - Search conversations
   - Pinned facts panel per conversation
4. Source panel (right sidebar, togglable):
   - Shows source documents used in last response
   - Document preview with highlighted relevant sections
   - Source quality tier indicator
Sprint 3.3: Data Import Interface
Claude Code Prompt:
Build the data import / library management interface:

1. Drag-and-drop zone:
   - Full-page drop zone that accepts files and folders
   - Visual feedback during drag (highlight border)
   - Progress bar for processing
   - Support for: PDF, PNG, JPG, TIFF, TXT, MD, HTML, .c, .h, .py, .asm, .bin, .csv, .xlsx
2. Library view:
   - Grid/list toggle for all imported documents
   - Filter by: document type, source tier, date imported, project
   - Search within library metadata
   - Document preview panel
   - Manual source tier assignment
3. Batch import:
   - Folder selection dialog
   - Recursive import with file type filtering
   - Import progress with per-file status
4. Document detail view:
   - Full document preview
   - Extracted text/data preview
   - Chunk visualisation
   - Metadata editor (tags, tier, notes)
Phase 4: Advanced Features & Polish (Weeks 7–10)
Sprint 4.1: System Architecture Mapping
Claude Code Prompt:
Build a system architecture characterisation module in /core/architecture/:

1. Component extraction:
   - From ingested datasheets, schematics, and manuals, extract:
     - Component names and types (processors, memory, sensors, filters, fuses)
     - Interface types (SPI, I2C, UART, GPIO, Ethernet, etc.)
     - Protocols (Modbus, OPC-UA, MQTT, proprietary)
     - Software components (OS, firmware versions, libraries)
2. Relationship mapping:
   - Build a graph of component relationships
   - Map interfaces between components
   - Identify communication pathways
3. Architecture summary generation:
   - Use LLM to generate natural-language system architecture description
   - Include component hierarchy
   - Flag areas where information is incomplete
4. Visualisation:
   - Simple interactive component diagram (React Flow or similar)
   - Click on components to see associated source documents
   - Export as image or structured data (JSON)
Sprint 4.2: Report Generation
Claude Code Prompt:
Build report generation in /core/reports/:

1. Report templates:
   - Product Overview Report
   - Component Analysis Report
   - System Architecture Report
   - Vulnerability Surface Summary
2. Report generation:
   - Compile from conversation history, architectural data, and source library
   - LLM-assisted narrative generation with source citations
   - Include confidence scores and data gaps
3. Export formats:
   - PDF (using reportlab or weasyprint)
   - Markdown
   - JSON (structured data export)
4. API endpoints:
   - POST /api/v1/reports/generate
   - GET /api/v1/reports/{id}
   - GET /api/v1/reports/{id}/export?format=pdf
Sprint 4.3: User Profiling & Adaptation
Claude Code Prompt:
Build user profiling and adaptation in /core/profile/:

1. Implicit profile building:
   - Track query patterns, frequently accessed topics, preferred detail level
   - Learn preferred output format (concise vs detailed, tables vs prose)
   - Track trusted/distrusted source preferences
2. Proactive suggestions:
   - When new documents are ingested that relate to the user's current investigation, surface a notification
   - Suggest related queries based on research patterns
3. Personalised system prompts:
   - Adapt LLM system prompt based on user profile
   - Include relevant domain context based on user's research focus
4. Profile management:
   - View and edit learned preferences
   - Reset profile
   - Export/import profiles
Phase 5: Testing, Hardening & Deployment (Weeks 10–12)
Sprint 5.1: Integration Testing & Performance
Claude Code Prompt:
Create comprehensive test suites:

1. Integration tests:
   - Full pipeline: ingest → index → query → response with validation
   - Conversation resumption after simulated time gap
   - Batch import of 500+ documents followed by queries
   - Multi-project isolation testing
2. Performance benchmarks:
   - Query response time with varying dataset sizes (100, 500, 2000, 5000 documents)
   - Ingestion throughput (documents per minute)
   - Memory usage profiling
   - Disk space usage reporting
3. Edge cases:
   - Corrupted PDF handling
   - Very large files (100MB+)
   - Non-UTF-8 encoded files
   - Empty documents
   - Binary files
4. Offline verification:
   - Disconnect network and run full test suite
   - Verify no network calls attempted (monitor with network logging)
Sprint 5.2: Packaging & Deployment
Claude Code Prompt:
Create offline deployment package:

1. Installer creation:
   - Tauri NSIS installer for Windows
   - AppImage or .deb for Linux
   - Bundle Python runtime (embedded Python or PyInstaller)
   - Bundle Ollama binary
   - Include a default lightweight model (e.g., Mistral 7B Q4)
2. First-run experience:
   - Model download/selection wizard (from bundled models)
   - Sample project with test data to demonstrate capabilities
   - Quick start guide
3. Update mechanism:
   - Export/import data for migration
   - Model swap (bring your own model files via USB)
4. Documentation:
   - User guide (built into app as help section)
   - Administrator guide (deployment, configuration)
   - API documentation (auto-generated from FastAPI)

11. VERIFICATION CHECKLIST
For each phase, the following verification protocol should be followed:
CheckMethodPass CriteriaOffline operationDisable network adapter, run all featuresNo errors, full functionalityMulti-modal ingestImport PDF, image, code, datasheetAll correctly parsed and indexedQuery accuracy20 test queries with known answers>80% correct with proper citationsConfidence scoringMix of well-sourced and poorly-sourced queriesScores align with source qualityHallucination detection10 adversarial queries designed to elicit hallucination>70% caught and flaggedConversation memoryMulti-session conversation testContext correctly reconstructedPerformance2000 document datasetQuery response <10s on standard laptopSource attributionVerify cited sources exist and contain relevant info100% of citations verifiableUser profileUse tool for 20+ queries, check adaptationPreferences reflected in responsesInstallerClean machine installTool functional within 15 minutes of install

12. KEY TIMELINE & MILESTONES
WeekMilestoneDeliverable1-2FoundationWorking backend, document ingestion pipeline, basic LLM integration3-4Core RAGQuery engine, hybrid search, source citation, confidence scoring5ConversationsMemory management, multi-thread conversations, pinned facts5-7Desktop UITauri app, chat interface, drag-and-drop import, library view7-8ArchitectureComponent extraction, relationship mapping, system diagrams8-9AdvancedReports, user profiling, adaptation, non-English support10-11TestingIntegration tests, performance benchmarks, offline verification12DeliveryPackaged installer, documentation, handover to HMGCC for testing

13. RISK REGISTER
R1 — LLM Quality Offline: Quantized models may produce lower-quality responses than cloud models. Mitigation: Test multiple models early, allow model swapping, invest in prompt engineering.
R2 — OCR Accuracy on Schematics: Handwritten annotations and complex circuit diagrams may not OCR well. Mitigation: Combine OCR with image embedding for visual retrieval; allow manual annotation.
R3 — Performance on Laptop Hardware: Large datasets with local LLM inference may be slow without GPU. Mitigation: Optimise chunk sizes, use efficient quantization (Q4_K_M), implement response streaming.
R4 — 12-Week Timeline: Ambitious scope for a full TRL-6 tool. Mitigation: Strict MVP focus on essential requirements; desirable features as stretch goals only.
R5 — Multi-Modal Complexity: Wide variety of input formats increases parser maintenance. Mitigation: Start with PDF and images, add other formats incrementally.

14. BUDGET CONSIDERATIONS (£60,000)
Approximate allocation for 12 weeks:
Personnel (primary cost): ~£48,000 (covering 1-2 FTE developers across the build). Infrastructure & tooling (Ollama, local hardware for testing, software licenses): ~£4,000. Testing & validation (including domain expert review time): ~£4,000. Packaging, documentation & handover: ~£2,000. Contingency: ~£2,000.

This document provides a complete, end-to-end specification for scoping and building the Smart Personal Assistant for Security Researchers MVP. The Claude Code prompts in Section 10 are designed to be directly executable as sequential build instructions, with verification steps after each sprint to ensure quality gates are met. The architecture is deliberately designed around offline-first, local-LLM-driven principles to meet the core constraint of operating without internet connectivity in classified environments.