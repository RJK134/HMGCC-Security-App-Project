# SKILLS.md — Domain Knowledge & Technical Skills Reference

## Domain Context: Security Research on Industrial Control Systems

### What Security Researchers Do
Security researchers in the national security context examine procured industrial machinery
for vulnerabilities. This involves "tear-down" analysis — physically and digitally
deconstructing products to understand every component, interface, and potential attack surface.

### The Research Phase (What This Tool Targets)
Before deep analysis begins, researchers must gather and comprehend vast amounts of
open-source technical intelligence about the product and its components:

- **Vendor Manuals** — PDF/paper documentation shipped with the product
- **Datasheets** — Component-level specifications from manufacturers (often PDF, tabular data)
- **Schematics** — Circuit diagrams, wiring diagrams, PCB layouts (images, CAD files)
- **Firmware/Source Code** — Vendor-supplied code, open-source libraries, binary blobs
- **Technical Forums** — Discussions on platforms about specific components, known issues, workarounds
- **Academic Papers** — Research on protocols, vulnerabilities, attack vectors
- **Photographs** — Tear-down images showing physical component placement and markings

### Industrial Control System (ICS) Specifics
ICS products are complex assemblies containing:

- **Physical Components:** Filters, fuses, processors, memory chips, sensors, actuators, relays, power supplies, connectors
- **Interfaces:** SPI, I2C, UART, JTAG, GPIO, Ethernet, RS-232, RS-485, CAN bus, USB
- **Protocols:** Modbus (RTU/TCP), OPC-UA, MQTT, BACnet, PROFINET, EtherNet/IP, DNP3, IEC 61850
- **Software:** Real-time operating systems (FreeRTOS, VxWorks, QNX), embedded Linux, firmware, bootloaders, proprietary control software
- **Multiple Processors:** A single product can contain several different microcontrollers and processors running different OSes

### Trust and Provenance in Security Research
Researchers assign different trust levels to information sources:
- **Highest trust:** Manufacturer official documentation, verified datasheets
- **High trust:** IEEE/IEC standards, peer-reviewed academic papers
- **Medium trust:** Established technical forums, known expert analysis
- **Lower trust:** Anonymous forum posts, unverified blog content, AI-generated content

This trust hierarchy is critical. The tool must surface provenance clearly.

## Technical Skills: RAG for Offline Technical Documents

### Retrieval-Augmented Generation (RAG) Pattern
RAG combines document retrieval with LLM generation to produce grounded, cited answers:

1. **Ingest** → Parse documents into text chunks with metadata
2. **Embed** → Convert chunks into vector representations
3. **Store** → Save vectors + metadata in a vector database
4. **Query** → Convert user question into vector, search for similar chunks
5. **Augment** → Assemble retrieved chunks into an LLM prompt as context
6. **Generate** → LLM produces answer grounded in the provided context
7. **Validate** → Check response against retrieved evidence, score confidence

### Hybrid Search Strategy
This project uses Reciprocal Rank Fusion (RRF) to merge two search strategies:

**Vector Search (Semantic):** Best for conceptual queries like "How does the PLC communicate with the HMI?" Captures meaning even when exact words differ.

**BM25 Keyword Search:** Best for specific lookups like "STM32F407VGT6 datasheet" or "Modbus register address 40001". Exact term matching is critical for part numbers, addresses, and protocol specifics.

**RRF Formula:** For each document `d`, the fused score is:
`RRF(d) = Σ 1 / (k + rank_i(d))` where `k` is typically 60 and `rank_i(d)` is the rank of `d` in result list `i`.

### Semantic Chunking
Naive fixed-size chunking destroys document structure. Use semantic chunking:

- Split on natural boundaries: headings, paragraphs, section breaks
- Respect table boundaries (keep tables as single chunks with structured representation)
- Code blocks remain intact (function-level chunking)
- Overlap between chunks (50-100 tokens) to preserve context at boundaries
- Each chunk carries metadata: source file, page, section heading, chunk index

### Local LLM Considerations
Quantised models (Q4_K_M, Q5_K_M) running on CPU have limitations:
- Context window: typically 4096-8192 tokens (much less than cloud models)
- Response quality: good for factual Q&A when context is well-assembled, weaker for complex reasoning
- Speed: 5-15 tokens/second on CPU, 30-100+ on GPU
- Mitigation: excellent prompt engineering, precise context assembly, response streaming

### Prompt Engineering for Security Research RAG
System prompts must instruct the local LLM to:
- Always cite sources using [Source: filename, page X] format
- State when information is uncertain or conflicting
- Never fabricate component specifications or technical details
- Present alternative interpretations when evidence is ambiguous
- Flag when the available context is insufficient to answer confidently

## Technical Skills: Document Processing

### PDF Processing (PyMuPDF/fitz)
- Extract text preserving reading order
- Handle multi-column layouts common in datasheets
- Extract embedded images (schematics, diagrams)
- Parse tables into structured data
- Handle encrypted/protected PDFs gracefully (skip, log warning)

### OCR (Tesseract)
- Pre-process images: deskew, denoise, binarize for optimal OCR
- Support for technical documents: component markings, handwritten annotations
- Expected accuracy: 85-95% on printed text, 60-80% on handwriting
- Post-processing: spell-check against technical dictionary

### Code Parsing (tree-sitter)
- Parse C, Python, assembly, shell scripts
- Extract: function signatures, struct definitions, constants, comments
- Build call graphs for firmware analysis
- Identify: imported libraries, compiler directives, memory addresses

### Schematic/Diagram Processing
- Component identification from circuit diagrams (future: ML-based)
- For MVP: OCR text from diagrams + store images with metadata for visual reference
- Allow manual annotation (user adds notes to images)

## Technical Skills: Confidence & Validation

### Confidence Scoring Model
Score each response 0-100 based on:
- **Source count:** More corroborating sources → higher confidence
- **Source quality:** Tier 1 sources weighted 3x vs Tier 4
- **Consistency:** All sources agree → boost. Contradictions → penalty
- **Coverage:** Query fully answered → boost. Partial answer → penalty
- **Recency:** More recent sources slightly preferred for technology topics

### Hallucination Detection
Compare each factual claim in the LLM response against retrieved chunks:
1. Extract claims from response (using LLM or heuristic parsing)
2. For each claim, check if supporting evidence exists in retrieved chunks
3. Flag unsupported claims with "NOT FOUND IN SOURCES" warning
4. Flag contradicted claims with "CONFLICTS WITH SOURCE: [details]"

## Technical Skills: Offline Desktop Application

### Tauri 2.x
- Rust-based desktop framework (much lighter than Electron)
- WebView2 on Windows, WebKitGTK on Linux
- File system access via Tauri API (drag-and-drop, file dialogs)
- IPC between React frontend and Rust/Python backend
- Builds as single executable with embedded assets

### State Management Pattern
- Zustand store for UI state (current project, active conversation, sidebar state)
- TanStack Query for server state (documents, conversations, query results)
- Optimistic updates for chat messages (show immediately, confirm with backend)
- Streaming responses via Server-Sent Events (SSE) for LLM output

## Technical Skills: Data Schema

### SQLite Schema (Key Tables)
```sql
projects(id, name, description, created_at, updated_at)
documents(id, project_id, filename, filepath, filetype, size_bytes, status, source_tier, import_timestamp, metadata_json)
chunks(id, document_id, content, chunk_index, page_number, section_heading, token_count, chroma_id)
conversations(id, project_id, title, summary, created_at, updated_at, last_accessed)
messages(id, conversation_id, role, content, citations_json, confidence_score, created_at)
pinned_facts(id, conversation_id, content, source_refs_json, created_at)
user_profiles(id, preferences_json, query_history_summary, created_at, updated_at)
source_tiers(document_id, tier, assigned_by, assigned_at)
```

### ChromaDB Collections
- One collection per project: `project_{project_id}_chunks`
- Metadata on each vector: `document_id`, `chunk_index`, `page_number`, `section_heading`, `document_type`, `source_tier`
- Embedding model must remain consistent within a collection (do not mix models)
