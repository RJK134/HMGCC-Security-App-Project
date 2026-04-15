CONSOLIDATED TEST REPORT: Security Research Assistant v0.1.0
Testing Summary
Date: April 15, 2026
Tool Version: v0.1.0
Testing Scope: End-to-end persona-based functional testing
Personas Tested:

✅ Persona 1: Lead Security Assessor (Primary workflow)

✅ Persona 2: Facility Security Officer (Report consumer — tested via report export)

⚠️ Personas 3-5: Not fully tested due to critical blocker bugs

CRITICAL BUGS (P0 — Must Fix)
BUG-001: Sources Panel Cannot Be Closed
Severity: CRITICAL
Impact: Blocks all subsequent use of the application
Affected Personas: All

Description:
Once the Sources sidebar is opened by clicking the "Sources" button, there is no way to close it. The panel:

Has no visible X or close button

Does not close when clicking outside the panel

Does not close with Escape key

Persists across page navigation

Persists across page refreshes (stored in localStorage/session)

Blocks access to chat input and conversation content

Reproduction:

Ask a question to trigger a response

Click "Sources" button in conversation header

Try to close the sources panel → impossible

Expected: Sources panel should have a close button or toggle behavior
Actual: Panel becomes permanently visible, blocking UI

Evidence:

BUG-002: Citation Filenames Show "unknown" Instead of Document Names
Severity: HIGH
Impact: Citations are not traceable to source documents — fails ER-02 requirement
Affected Personas: Lead Assessor, FSO, Dstl Researcher

Description:
4 out of 5 citations in a test query showed filename as "unknown" instead of the actual document name. Only 1 citation correctly showed "NIST_SP_800-82_ICS_Security.pdf". This makes it impossible to trace findings back to specific source documents, which is a core requirement for security assessments.

Reproduction:

Import documents with recognizable filenames (e.g., "Crompton_RS485_Spec.pdf")

Ask a query that retrieves from these documents

Check citations in response footer

Observe: majority show "unknown p.X" instead of filename

Expected: All citations should show {DocumentName}.pdf p.{PageNumber}
Actual: Most show unknown p.{PageNumber}

Evidence: (citations showing "unknown p.6", "unknown p.17", "unknown p.4", "unknown p.136")

Root Cause Hypothesis: Document metadata (filename) not being stored or retrieved correctly during ingestion/indexing

BUG-003: Settings Shows Incorrect Document Count for New Projects
Severity: MEDIUM
Impact: Misleading information, user confusion
Affected Personas: Lead Assessor

Description:
When creating a brand new project ("AM-2026-Assessment-SN4471") with 0 documents imported, the Settings page shows "Documents indexed: 58" — the count from the previously active project (ICS Product Assessment).

Reproduction:

Switch to a project with N documents (e.g., ICS Product Assessment with 58 docs)

Create a new project

Navigate to Settings

Observe: Shows "Documents indexed: 58" despite Library showing "0 of 0 documents"

Expected: Settings should show "Documents indexed: 0" for new empty project
Actual: Shows document count from previous project

Evidence: — Settings showing 58 docs for empty project

BUG-004: Backend Connection Errors on Page Navigation
Severity: MEDIUM (Intermittent)
Impact: User sees error banner, unclear if feature will work
Affected Personas: All

Description:
When navigating between sections (Chat → Architecture, Chat → Reports), a red error banner appears:

"Backend not connected. Start the backend server to use the application"

The error resolves itself after 2-3 seconds, but it creates uncertainty and looks unprofessional. This suggests:

Backend WebSocket/polling connection is being dropped on navigation

Frontend is not maintaining connection state correctly

Or backend is slow to respond to keepalive pings

Reproduction:

Navigate from Chat to Architecture page

Observe: Red error banner appears at top

Wait 2-3 seconds → error clears automatically

Expected: No error banner if backend is running and connected
Actual: Transient "backend not connected" error appears

Evidence:

HIGH PRIORITY BUGS (P1)
BUG-005: LLM Hallucinates Project Context in Reports
Severity: HIGH
Impact: Reports contain fabricated information — fails credibility test for FSO persona
Affected Personas: Lead Assessor, FSO

Description:
The Investigation Summary Report contains fabricated project details not present in any source documents:

Project name: "SecureNet project"

Date range: "Jan 15 - Mar 31, 20XX"

Document references: "Documents 1-7" with fictional names like "Project Briefing Document", "Data Access Agreement"

These details are hallucinated by the LLM and not grounded in the actual imported documents. This violates the fundamental requirement that responses must be "grounded in your imported documents."

Reproduction:

Generate an Investigation Summary Report

Export as MARKDOWN or HTML

Review the "Investigation Overview" section

Observe: Fabricated project name, dates, and document inventory

Expected: Report should only reference actual imported documents and should not invent project metadata
Actual: Report invents plausible-sounding but fictitious project context

Evidence: — Report showing "SecureNet project (Dates: Jan 15 - Mar 31, 20XX)"

Impact on Personas:

FSO: Cannot trust report for decision-making if it contains fabricated data

Lead Assessor: Report would fail audit/peer review

BUG-006: Source Tier Selection UI/UX Unclear
Severity: MEDIUM
Impact: User confusion about how to assign source quality tiers
Affected Personas: Lead Assessor

Description:
The source tier selector buttons (Manufacturer, Academic, Trusted Forum, Unverified) have unclear interaction design:

When you click "Manufacturer", it highlights with a ring border

But "Unverified" also stays visually active

It's unclear if this is multi-select or single-select

No confirmation of which tier will be applied to the next document upload

Reproduction:

Go to Library page for a new project

Click "Manufacturer" button

Observe: Both "Manufacturer" and "Unverified" appear selected

Expected: Clear single-selection radio button behavior with visual confirmation
Actual: Ambiguous multi-selection-like appearance

Evidence:

BUG-007: File Import Dialog Opens and Closes Immediately
Severity: LOW (Expected in automated testing, but worth documenting)
Impact: Cannot test file import flow in automated environment
Affected Personas: Lead Assessor

Description:
When clicking the "Drag files here or click to browse" upload area, the OS file dialog opens but immediately closes. This is expected in Tauri apps during automated testing but prevents testing the full import workflow.

Note: This is not necessarily a bug in production, but should be noted for testing limitations.

RAG QUALITY ISSUES (Not bugs, but enhancement areas)
ISSUE-001: Generic Responses vs. Device-Specific Analysis
Severity: MEDIUM
Impact: Reduces tool value for device-specific assessments
Affected Personas: Lead Assessor, Procurement Officer

Description:
Query: "What is the complete hardware architecture of this system?"

Response provided a generic description of ICS hardware architecture (ICs, gate-level characterization, Trojan horses, etc.) rather than analyzing the specific device being assessed based on its manufacturer documentation.

The retrieval appears to have pulled academic papers about ICS security theory rather than device-specific datasheets/manuals.

Root Cause Hypothesis:

Retrieval is not prioritizing "Manufacturer" tier sources over "Academic" sources

Or: Query embedding is too generic and matches broad ICS theory content

Or: No device-specific manufacturer docs were imported in this test set

Recommendation:

Implement source-tier-weighted retrieval (Manufacturer docs should score higher than Academic for architecture queries)

Add query rewriting to inject context like "based on the imported manufacturer documentation for [product]"

ISSUE-002: No Visual Loading State for Long-Running Queries
Severity: LOW
Impact: User uncertainty during 60-120 second wait times
Affected Personas: All

Description:
When a query is processing, the only indicator is a blinking cursor in the response area. For queries that take 60-120 seconds on CPU (as expected with Mistral 7B on mid-range hardware), users have no indication of:

Progress (0-100%)

Which stage of processing (retrieval vs generation)

Estimated time remaining

Recommendation:

Add a progress indicator showing "Searching documents... (10%)" → "Generating response... (60%)" with estimated time

Or stream response tokens in real-time so users see partial output

ENHANCEMENTS (Nice-to-have)
ENHANCE-001: Add Pin Icon Visibility on Hover
Description: The user tip says "Hover over responses to pin key findings" but hovering over responses showed no pin icon in testing. The pin icon only appeared after clicking certain areas.

Recommendation: Make pin action more discoverable with a persistent or hover-triggered pin button on each response card.

ENHANCE-002: Add Conversation Deletion/Management
Description: The conversation list shows all past conversations but no way to delete, rename, or archive them.

Recommendation: Add right-click context menu or hover actions for conversation management (Delete, Rename, Archive).

ENHANCE-003: Add OFFICIAL Classification to Report Header
Description: The UI footer shows "OFFICIAL" classification marking, but the exported reports (MARKDOWN/HTML) don't include this marking in headers/footers.

FSO Persona Requirement: "Does the OFFICIAL classification marking appear on every page?"

Recommendation: Add classification marking to all report export formats in header/footer on every page.

ENHANCE-004: Implement Architecture Extraction Visual Feedback
Description: Clicking "Extract Architecture" button showed no loading state, progress indicator, or completion confirmation.

Recommendation: Show extraction progress with stages: "Analyzing documents... → Identifying components... → Building graph → Complete"

ENHANCE-005: Add Report Preview Before Export
Description: Clicking MARKDOWN/PDF/JSON/HTML export buttons triggers immediate download with no preview.

FSO Persona Requirement: Being able to review the report before finalizing export.

Recommendation: Add a "Preview" button that opens report in a modal/new tab before committing to download.

PERSONA-SPECIFIC FINDINGS
Persona 1: Lead Security Assessor
Successfully Completed:

✅ Created new project with proper naming convention

✅ Submitted complex technical query

✅ Received cited response with confidence score (74/100)

✅ Sources sidebar shows match percentages

✅ Can expand source excerpts for verification

Blocked/Failed:

❌ Cannot continue multi-query workflow due to Sources panel blocking UI

❌ Cannot trace citations to source documents (unknown filenames)

❌ Cannot use Architecture extraction (no visible output)

⚠️ Response quality is generic rather than device-specific

Critical Path Issues:

BUG-001 (Sources panel) is a showstopper — user cannot conduct systematic investigation across multiple threaded queries as specified in persona workflow

Persona 2: Facility Security Officer
Report Evaluation (based on Investigation Summary export):

FSO Criteria	Status	Notes
Executive summary understandable by board	✅ PASS	Overview section is clear and non-technical
All vulnerabilities rated by severity	⚠️ PARTIAL	No vulnerabilities explicitly listed with CVSS scores
Can trace findings to source documents	❌ FAIL	Citations present but 80% show "unknown" filename
Mitigations practical and costed	⚠️ PARTIAL	Mitigations mentioned but not costed
Acceptable vs unacceptable risks identified	❌ FAIL	No risk categorization framework
OFFICIAL marking on every page	❌ FAIL	Not present in MARKDOWN export
Critical Issue: BUG-005 (hallucinated project context) means FSO cannot trust the report as an authoritative document. The fabricated "SecureNet project" details would fail an audit.

Persona 3-5: Not Fully Tested
Due to BUG-001 blocking continued interaction, I was unable to complete the following persona workflows:

Persona 3 (Procurement Officer): Decision-support queries requiring mitigation cost/complexity analysis

Persona 4 (HMGCC Evaluation Panel): End-to-end scoring against ER-01 through ER-08 requirements

Persona 5 (Dstl Researcher): RAG stress-testing with contradiction detection and meta-queries

REQUIREMENTS COMPLIANCE (Partial Assessment)
Based on limited testing completed:

Requirement	Status	Evidence/Notes
ER-01: Offline operation	✅ PASS	No internet connectivity required; Ollama runs locally
ER-02: Cited responses	⚠️ PARTIAL	Citations present but 80% show "unknown" filename (BUG-002)
ER-03: Confidence scoring	✅ PASS	74/100 score shown with "Good" label
ER-04: Source tier support	⚠️ PARTIAL	UI supports 4 tiers but selection UX unclear (BUG-006)
ER-05: Multi-format export	✅ PASS	MARKDOWN, PDF, JSON, HTML options available
ER-06: Conversation threading	⚠️ BLOCKED	Cannot test due to BUG-001
ER-07: Architecture extraction	⚠️ UNKNOWN	Feature exists but no visible output when tested
ER-08: Report generation	⚠️ PARTIAL	Works but contains hallucinated content (BUG-005)
RECOMMENDATIONS FOR REMEDIATION
Immediate (Pre-Demo)
Fix BUG-001 (Sources panel close) — Add close button and prevent localStorage persistence

Fix BUG-002 (Unknown filenames) — Debug document metadata storage/retrieval

Fix BUG-005 (Hallucinated content) — Constrain report generation prompts to grounded-only content

Short-term (Phase 1 Release)
Address BUG-003, BUG-004, BUG-006 (Settings count, backend errors, source tier UX)

Implement ENHANCE-001 (pin icon visibility)

Implement ENHANCE-003 (OFFICIAL marking in exports)

Add ENHANCE-002 (conversation management)

Medium-term (Phase 2)
Address ISSUE-001 (RAG source tier weighting for better device-specific responses)

Implement ISSUE-002 (progress indicators for long queries)

Add ENHANCE-004 (architecture extraction feedback)

Add ENHANCE-005 (report preview)

OVERALL ASSESSMENT
Strengths:

Core RAG pipeline functions and returns relevant content

Offline operation with local Mistral 7B model works

Report generation produces professional-looking structured output

Source tier UI shows good conceptual design

Confidence scoring provides useful metadata

Critical Weaknesses:

Sources panel bug makes the