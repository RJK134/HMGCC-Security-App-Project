Tester: Claude (Automated Persona Testing via Browser Extension)

EXECUTIVE SUMMARY
The application shell, navigation, settings, and backend API health are broadly functional. However, a critical blocking bug — the complete absence of the Projects CRUD API — prevents the core user workflow from functioning. No documents can be imported, no queries can be sent, and no conversations can be created because they all depend on having a project selected first. This must be fixed before any further feature testing can proceed.

TEST PERSONAS
Persona 1 — "Alicia" (First-Time Security Researcher): New user attempting the core workflow: create project → import documents → ask questions → get answers
Persona 2 — "Ben" (Power User / Returning Researcher): Experienced user testing advanced features: conversations, architecture, reports, profiling
Persona 3 — "Claire" (IT Administrator): Testing settings, system health, deployment, and configuration

BUG REPORT
BUG-001: CRITICAL — Projects API Endpoint Missing (BLOCKER)
Severity: CRITICAL — Blocks all core functionality
Persona: All personas
Steps to Reproduce:

Open app at localhost:1420
Click "Select Project" dropdown
Click "New Project"
Enter project name
Click "Create"

Expected: Project is created, project selector updates to show the new project, user can proceed to import documents and chat.
Actual: API returns 404. Console error: ApiError: Request failed: 404 on createProject (client.ts:24). The backend has no /api/v1/projects endpoint at all. Verified via OpenAPI spec — the paths object contains health, documents, query, conversations, architecture, reports, profile, notifications, and maintenance endpoints, but zero project endpoints.
Root Cause: The backend router (backend/api/v1/router.py) does not include a projects sub-router. The backend/api/v1/projects.py file is either missing or not registered.
Impact: Without project creation, the entire application is non-functional. Every page (Chat, Library, Architecture, Reports) shows "Select a project" and cannot proceed. This is a complete blocker for ALL user workflows.
Frontend behaviour after failure: The dropdown closes silently with no error message shown to the user. The project selector still shows "Select Project". No toast, no alert, no indication that creation failed. The form retains the old project name if reopened.

BUG-002: HIGH — No User-Facing Error on Project Creation Failure
Severity: HIGH
Persona: Alicia (first-time user)
Steps to Reproduce: Same as BUG-001
Expected: If project creation fails, show a clear error message such as "Failed to create project. Please check backend connection."
Actual: The dropdown silently closes. No feedback. User has no idea what happened and will repeatedly try without understanding why it fails.
Fix Required: Add error handling in the ProjectSelector component. Catch the ApiError from createProject, show a toast notification or inline error.

BUG-003: MEDIUM — Project Creation Form Missing Description Field
Severity: MEDIUM
Persona: Alicia
Observation: The project creation form only has a "Project name" field. Per the specification (ARCHITECTURE.md, API endpoints), the createProject endpoint should accept both name and description. The form lacks a description input.
Fix Required: Add an optional description textarea to the project creation dropdown form.

BUG-004: LOW — Project Name Truncation in Creation Form
Severity: LOW — Cosmetic
Persona: Alicia
Steps to Reproduce: Enter a long project name like "ICS Product Assessment - Additive Manufacturing Unit"
Actual: The text is visually truncated in the input field. The full name is accepted but the user can't see the complete name while typing.
Fix Required: Either widen the dropdown form or allow the input to scroll horizontally with visible overflow indication.

FUNCTIONAL ASSESSMENT BY PAGE
Chat Page — BLOCKED
Status: Cannot test — requires a selected project
Observations:

Empty state message "Select or create a project to start chatting." is displayed correctly
No chat input area, message list, or conversation sidebar visible without a project (correct behaviour)
URL correctly updates to /chat when navigating

Items unable to test: Streaming query, citation badges, confidence bars, flagged claims, conversation memory, source panel, conversation sidebar, new conversation creation, pinned facts

Library Page — BLOCKED
Status: Cannot test — requires a selected project
Observations:

Empty state message "Select a project to view its document library." displayed correctly
No drop zone, document grid, or import controls visible without a project (correct behaviour)
URL correctly updates to /library

Items unable to test: Drag-and-drop upload, batch import, document grid/list views, source tier selector, document detail page, document preview, chunk browser

Architecture Page — BLOCKED
Status: Cannot test — requires a selected project
Observations:

Empty state message "Select a project to view its system architecture." displayed correctly
URL correctly updates to /architecture

Items unable to test: Extract architecture trigger, component list, interface map, architecture summary, gap identification

Reports Page — BLOCKED
Status: Cannot test — requires a selected project
Observations:

Empty state message "Select a project first." displayed correctly
URL correctly updates to /reports

Items unable to test: Report type selector, report generation, report viewer, PDF/Markdown/JSON export

Settings Page — FUNCTIONAL ✓
Status: Working correctly
Observations:

LLM Model section: Shows "Available Models" dropdown with mistral:7b-instruct-v0.3-q4_K_M selected. "Ollama status: Connected" displayed correctly.
Retrieval Settings: All four fields present and editable — Top-K Results (10), Chunk Size (512), Chunk Overlap (50), Max Context Tokens (4096). Default values match specification.
Appearance: Theme toggle between Light and Dark works. Both buttons styled correctly. Active theme highlighted in blue.
About section: Shows "Security Research Assistant v0.1.0" and "HMGCC Co-Creation Challenge (CH-2026-001)"

Missing elements (per spec):

No "Save Settings" button — unclear if settings auto-save or require explicit save
No "Reset to Defaults" button
No embedding model configuration (spec calls for separate embed model selection)
No reranking toggle (on/off)
No profile/preference section (may be on a separate Profile page not yet built)


Navigation & Layout — FUNCTIONAL ✓
Status: Working correctly with minor issues
Observations:

Sidebar navigation: All 5 items present (Chat, Library, Architecture, Reports, Settings) with correct icons
Active page highlighted in blue with background highlight
Sidebar collapse: Works correctly — collapses to icon-only mode, content area expands
Top bar: Project selector, notification bell, health indicator, theme toggle all present
Health indicator: Green dot with tooltip "All systems OK (0 docs)" — correctly reflects backend status
Theme toggle: Switches between sun (light) and moon (dark) icons — works correctly
Notification bell: Opens dropdown showing "No notifications." with close X — works correctly
OFFICIAL classification marking: Displayed at bottom footer — correct per requirement
URL routing: Correctly updates URL path on navigation (/chat, /library, /architecture, /reports, /settings)

Minor issues:

No "Security Research Assistant" title visible in the top bar (only the shield icon and a small icon that might be the logo)
The sidebar lacks a conversation list section below the navigation (specified in Sprint 3.2)


Backend API — PARTIALLY FUNCTIONAL
Status: Running with critical gap
Health endpoint: Returns {"status":"ok","ollama_connected":true,"available_models":["mistral:7b-instruct-v0.3-q4_K_M","nomic-embed-text:latest"],"database_ok":true,"vector_store_ok":true,"document_count":0}
Verified endpoints present (via OpenAPI):

Health: GET /api/v1/health ✓
Documents: POST upload, POST batch, GET list, GET single, DELETE, PATCH tier ✓
Query: POST /api/v1/query, POST /api/v1/query/simple ✓
Conversations: full CRUD + pins + suggest-pins + summarise ✓
Architecture: GET + POST extract ✓
Reports: POST generate, GET list, GET single, GET export ✓
Profile: GET, PUT preferences, GET export, POST import ✓
Notifications: GET ✓
Maintenance: GET version, POST export, POST import ✓

MISSING endpoints:

Projects CRUD: POST, GET list, GET single, DELETE — ALL MISSING ← CRITICAL


REMEDIATION PROMPTS FOR CLAUDE CODE
The following prompts should be executed in order to fix the identified issues:
Remediation Prompt 1: Add Projects API (CRITICAL — Execute First)
CRITICAL BUG FIX: The backend is missing the entire Projects API. The frontend calls POST /api/v1/projects to create a project, GET /api/v1/projects to list them, GET /api/v1/projects/{id} to get one, and DELETE /api/v1/projects/{id} to delete one. These endpoints do not exist — the backend returns 404.

Read CLAUDE.md and ARCHITECTURE.md for context.

Fix this by:

1. Verify that core/database/repositories/project_repo.py exists with ProjectRepository class (create, get_by_id, list_all, update, delete methods). If not, create it.

2. Create backend/api/v1/projects.py with these endpoints:
   - POST /api/v1/projects
     Body: { "name": str, "description": str (optional) }
     Creates a new project in SQLite
     Returns the full Project model with id, name, description, created_at, updated_at, document_count=0, conversation_count=0

   - GET /api/v1/projects
     Returns list of all projects
     Each project includes document_count and conversation_count

   - GET /api/v1/projects/{project_id}
     Returns single project by UUID
     404 if not found

   - PUT /api/v1/projects/{project_id}
     Update name and/or description
     Returns updated project

   - DELETE /api/v1/projects/{project_id}
     Delete project and all associated data (documents, conversations, chunks, vectors)
     Returns 204 No Content

3. Register the projects router in backend/api/v1/router.py:
   Import the projects router and include it with prefix="/api/v1" and tags=["projects"]

4. Verify the projects table exists in the SQLite schema (core/database/schema.py).
   If not, add: CREATE TABLE IF NOT EXISTS projects (id TEXT PRIMARY KEY, name TEXT NOT NULL, description TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)

5. Add the dependency injection for project repository in backend/dependencies.py.

6. Write tests in tests/test_projects_api.py:
   - Test POST creates project and returns it with UUID id
   - Test GET list returns created projects
   - Test GET by id returns correct project
   - Test DELETE removes project
   - Test POST with empty name returns 422 validation error
   - Test GET nonexistent id returns 404

VERIFICATION:
1. curl -X POST http://localhost:8000/api/v1/projects -H "Content-Type: application/json" -d '{"name":"Test Project"}' — returns 200/201 with project data
2. curl http://localhost:8000/api/v1/projects — returns list including the created project
3. Open the frontend, click Select Project > New Project > enter name > Create — project is created and auto-selected
4. All pages (Chat, Library, Architecture, Reports) now show project-specific content instead of "Select a project" messages
Remediation Prompt 2: Add Error Handling for Project Creation UI
BUG FIX: When project creation fails (API error), the frontend silently closes the dropdown with no error feedback. The user has no idea the operation failed.

Fix in frontend/src/components/projects/ProjectSelector.tsx (or wherever the project dropdown/form is implemented):

1. Wrap the createProject API call in try/catch
2. On error, show a visible error message:
   - If 404: "Backend API error — projects endpoint not found. Check backend version."
   - If 500: "Server error creating project. Please try again."
   - If network error: "Cannot connect to backend. Ensure the server is running."
3. Display the error as either:
   - An inline red error message below the Create button in the dropdown form
   - OR a toast notification that appears at the top/bottom of the screen
4. Keep the form open with the entered data so the user can retry after fixing the issue
5. Add a loading state to the Create button (spinner/disabled) while the API call is in progress

VERIFICATION:
1. Temporarily break the projects endpoint (or if not yet fixed, test against the current 404)
2. Click Create — see a clear error message instead of silent failure
3. Fix the endpoint, click Create again — project creates successfully
Remediation Prompt 3: Add Project Description Field to Creation Form
ENHANCEMENT: The project creation dropdown form only has a "Project name" input field. Per the specification, projects should also have an optional description.

Fix the project creation form component:

1. Add a second input field (textarea) below the project name input:
   - Label: "Description (optional)"
   - Placeholder: "Brief description of this investigation..."
   - Textarea: 2-3 rows, resizable
   - Optional — form should submit successfully with just a name

2. Pass both name and description to the createProject API call

3. Ensure the form resets both fields after successful creation

VERIFICATION:
1. Open project creation form — see both name and description fields
2. Create project with name only — succeeds
3. Create project with name + description — succeeds, description saved
Remediation Prompt 4: Add Missing Settings Features
ENHANCEMENT: The Settings page is missing several specified features.

Add the following to the Settings page (frontend/src/pages/SettingsPage.tsx):

1. SAVE BUTTON: Add a "Save Settings" button at the bottom of the Retrieval Settings section.
   Show a success toast "Settings saved" on successful save.
   Disable the button when no changes have been made (track dirty state).

2. RESET TO DEFAULTS BUTTON: Add a "Reset to Defaults" button next to Save.
   On click, restore: Top-K=10, Chunk Size=512, Chunk Overlap=50, Max Context Tokens=4096.
   Show confirmation dialog before resetting.

3. EMBEDDING MODEL: Add an "Embedding Model" dropdown in the LLM Model section.
   Should show available embedding models from Ollama (nomic-embed-text is currently available per the health endpoint).
   This is separate from the main inference model.

4. RERANKING TOGGLE: Add a toggle switch in Retrieval Settings:
   "Enable LLM Re-ranking" with a brief description: "Uses the LLM to re-score search results for higher accuracy. Slower but more precise."
   Default: enabled.

VERIFICATION:
1. Change a retrieval setting, click Save — value persists after page refresh
2. Click Reset to Defaults — all values return to defaults
3. Embedding model dropdown shows available models
4. Reranking toggle switches and persists
Remediation Prompt 5: Add Conversation Sidebar to Chat Page
ENHANCEMENT: The Chat page sidebar should show a list of conversations for the current project below the main navigation, per Sprint 3.2 specification.

Add to the sidebar (when on the Chat page and a project is selected):

1. Below the Settings nav item, add a divider line and a "Conversations" section header

2. Show a "New Conversation" button (plus icon + "New Chat" text)

3. Below, show a scrollable list of conversations for the current project:
   - Each item shows: conversation title (truncated), last message timestamp
   - Active conversation highlighted
   - Click to switch conversation
   - Group by: Today, Yesterday, This Week, Older

4. If no conversations exist, show: "No conversations yet. Start one below."

5. The conversation list should refresh when:
   - A new conversation is created
   - The project changes
   - A message is sent (updates timestamp/preview)

VERIFICATION:
1. Select a project, navigate to Chat
2. See "New Chat" button in sidebar
3. Create a conversation — it appears in the sidebar list
4. Create multiple conversations — they appear in chronological groups
5. Click between conversations — chat window updates

SUMMARY OF ALL ISSUES
IDSeverityCategoryDescriptionBlocked ByBUG-001CRITICALBackendProjects API endpoints completely missing (404)—BUG-002HIGHFrontendNo error feedback on failed project creation—BUG-003MEDIUMFrontendMissing project description field in creation form—BUG-004LOWFrontendLong project names truncated in creation form input—BUG-005MEDIUMFrontendSettings page missing Save button, Reset, Embed model, Reranking toggle—BUG-006MEDIUMFrontendChat sidebar missing conversation list sectionBUG-001BLOCKED—AllChat, Library, Architecture, Reports pages untestableBUG-001
Recommended Fix Order: BUG-001 (critical blocker) → BUG-002 → BUG-003 → BUG-005 → BUG-006 → BUG-004
Once BUG-001 is resolved, a second testing pass should be performed covering document ingestion, RAG queries, conversations, architecture extraction, report generation, and the full end-to-end workflow.
Here's my assessment as Alicia, structured as a field evaluation report for the SRA prototype.

Evaluation Context
The Security Research Assistant (SRA) is a locally-hosted, offline RAG application designed for the HMGCC Co-Creation Challenge (CH-2026-001). It aims to help security researchers characterise complex industrial machinery by ingesting, indexing, and querying technical documentation using local LLM-powered retrieval-augmented generation. The total challenge budget is up to £60,000, targeting TRL 6. The app runs as a Tauri desktop frontend backed by a Python/FastAPI backend using Ollama for local inference.

First Impressions — Cold Start
Opening the SRA at localhost:1420/chat, the first thing I see is an empty workspace: "No conversations yet" and a prompt to "Ask a question about your imported documents". This immediately raises several issues:

No onboarding or document import prompt. I have a stack of PDFs, firmware dumps, and datasheets ready to go. There's no visible "Import Documents" button, drag-and-drop zone, or guidance on how to populate the Library. The Library tab exists in the nav bar, but from the Chat view there's zero indication I need to go there first. A first-run wizard or even a banner saying "Import documents in Library to get started" would prevent this dead-end.

No project/case context. The header says "Trial Project 1" — presumably I should be able to create a named project (e.g., "AM-Machine-Assessment-2026-04") and scope my documents to it. Can I? How? Not obvious from here.

"OFFICIAL" classification marking is visible at the bottom, which is correct practice for UK government tooling and a good sign someone has thought about the deployment context.

Planned Investigation Workflow (What I'd Test)
As a researcher, my normal workflow would proceed in this sequence:

Bulk import — drag 40+ documents (PDFs, images, code files, forum HTML exports) into the tool

Broad characterisation query — "What is this product? Who manufactures it? What are the key subsystems?"

Citation verification — does every claim map to a specific document, page, and paragraph?

Cross-referencing — "Does the firmware version in the source code match the version listed in the vendor manual?"

Pinning findings — save key facts (model number, firmware hash, comms protocols) for later reference

Threaded investigation — open separate conversations for "Network Protocols," "Firmware Analysis," "Physical Interfaces"

Report generation — export findings with full citation chains

Blockers and Concerns
Document ingestion is invisible
The Library tab presumably handles imports, but from the Chat page there's no affordance. For a researcher under time pressure with 50+ documents, I need: batch import, format support indicators (does it handle .bin firmware? .jpg circuit photos? .pcap captures?), and ingestion status/progress. The README lists no supported file formats.

Citation granularity is critical
The chat interface promises "confidence scores" and source citations. This is the single most important feature for my workflow. I need to know:

Which document the answer came from (filename, not just "Source 1")

Which page/section within that document

The exact quoted passage so I can verify it wasn't hallucinated

Confidence score methodology — is it cosine similarity from the vector store? LLM self-assessment? Both?

Without being able to submit a query (no documents loaded), I can't verify any of this yet.

Conversation threading is present but untested
The sidebar shows a "New conversation" button and a conversations list. This aligns with my need for separate investigation threads. Key questions: Can I rename conversations? Can I move findings between threads? Can I search across all conversations?

Architecture and Reports tabs are promising
The nav includes Architecture and Reports sections. The Architecture view at localhost:1420/architecture appears in browsing history, suggesting it exists. Reports would be essential for my final deliverable — but I can't assess either without loaded data.

Offline-only is non-negotiable — and met
The README confirms "Fully offline. No internet required," using Ollama for local inference. This is a hard requirement for classified facility work. Good.

What Would Need to Work Before This Replaces My Current Workflow
Capability	Priority	Status
Bulk document import (PDF, images, code)	Critical	Unknown — not testable from Chat view
Granular source citations (doc + page + passage)	Critical	Claimed but unverifiable without documents 
Confidence scores on every response	High	Claimed 
Cross-document comparison queries	Critical	Unknown
Pinning/saving key findings	High	Unknown
Named conversation threads	Medium	UI exists 
Report export with citation chains	Critical	Reports tab exists but untested
Firmware/binary file analysis	Medium	Unknown format support
Image analysis (circuit photos)	Medium	Unknown — needs multimodal model
Immediate Recommendation
The SRA cannot be meaningfully evaluated from the Chat view alone in its current state. My next steps would be:

Navigate to Library to attempt document import and assess format support

Load a minimal test set (one PDF manual, one datasheet, one code file)

Run the broad characterisation query and rigorously check every citation

Attempt a cross-reference query between two documents

Test the Reports export

The architecture is sound for the challenge requirements — offline RAG with local LLM, source-grounded responses, project-scoped conversations. The critical unknown is execution quality: citation accuracy, retrieval relevance, and whether it handles the heterogeneous document types a real hardware teardown produces. The "OFFICIAL" classification banner and air-gapped design show the right security posture for the target environment.

Marcus's Usability Evaluation Report — Security Research Assistant v0.1.0
Persona: Marcus, Junior Security Researcher (6 months ICS experience, first time using AI research tools)
Application: Security Research Assistant v0.1.0, HMGCC Co-Creation Challenge (CH-2026-001)
Backend: Mistral 7B (q4_K_M quantised) via Ollama, fully offline
Date: 13 April 2026

Executive Summary
The SRA has promising architecture — a RAG-based document Q&A system with project management, conversation threading, confidence scoring, and report generation. However, from a junior researcher's perspective, the tool is not ready for unsupervised use. Multiple critical failures were observed including silent errors, missing UI features backed by existing API endpoints, dangerously ungrounded responses, and extreme latency that would make the tool impractical for real workflows.

Overall Score: 28/100 (Not Usable Without Supervision)

Test Results
Test 1: First-Time Experience
Rating: 4/10

No onboarding wizard, tutorial, or welcome guide

When opening an empty project, the "Start a conversation" prompt tells you to ask about imported documents — but gives no direction to import documents first

Sidebar icons are unlabeled when collapsed — a folder icon, people icon, document icon, and gear icon with no text

When expanded, labels (Chat, Library, Architecture, Reports, Settings) are clear

The "OFFICIAL" classification banner is present but unexplained

Missing: A "Getting Started" flow: Step 1 → Import documents, Step 2 → Ask questions

Test 2: Query Before Importing Documents
Rating: 1/10 — CRITICAL FAILURE

Typed "what is this system?" in an empty project (0 documents)

Loading spinner appeared, then disappeared

No response appeared at all — no error message, no "you need to import documents first" guidance, nothing

The page silently reverted to the "Start a conversation" empty state

A junior researcher would assume the tool is broken and give up

Recommendation: Display a clear message like "No documents imported yet. Go to Library to add your research files."

Test 3: Unsupported File Imports
Rating: 5/10 (Partial — could not test actual upload)

The upload zone says "PDF, images, code, text, spreadsheets" — no explicit file extension list

The "All Types" filter dropdown reveals supported categories: PDF, Image, Code, Text, Spreadsheet

No .docx support — a massive gap since Word documents are ubiquitous in government/defence

Source quality tags (Manufacturer, Academic, Trusted Forum, Unverified) are displayed with no explanation of what they mean or when to use each

"Unverified" is pre-selected by default — Marcus has no idea what this implies for search weighting

Recommendation: Add tooltips to source quality tags. Support .docx. List accepted extensions explicitly.

Test 4: Vague Question With Documents Present
Rating: 1/10 — CRITICAL FAILURE

Typed "tell me evrything about this" (deliberate typo) in a project with 50+ documents

Loading spinner appeared then disappeared

Same silent failure — no response, no error, page reverted to empty state

The typo "evrything" was not handled gracefully — no "did you mean?" suggestion

Two consecutive queries both failed silently, establishing a pattern of unreliable query submission

Test 5: Off-Topic Question (Weather)
Rating: 2/10 — SECURITY CONCERN

Asked "whats the weather like today?" — an obviously off-topic question

Response took approximately 2.5 minutes to generate — unacceptable for interactive use

The model acknowledged documents didn't contain weather info (good) but then generated Python code to call the OpenWeatherMap API — completely ungrounded and irrelevant

Referenced "an embedded vector database called 'Iron'" — a hallucination not present in any document

Suggested using external APIs on what is supposed to be an air-gapped system — potential security concern

The response appeared twice (12:38 AM and 12:44 AM) — duplicate response rendering bug

Confidence score was 59/100 "Medium" — far too high for a completely off-topic, hallucinated response

Recommendation: Implement off-topic detection. If a query has no relevance to imported documents, respond with "This question doesn't appear to relate to your imported documents" instead of fabricating an answer.

Test 6: Confidence Score Explanation
Rating: 5/10

Clicking the "59/100 Medium" score expands a tooltip — good discoverability

The explanation shows: "Based on 10 source chunk(s) from 6 documents. Source tiers: Unverified / General Source: 10. 0/2 claims supported"

Issues for Marcus:

"source chunk(s)" is unexplained jargon

"Source tiers: Unverified / General Source" means nothing without context

"0/2 claims supported" is useful but buried in technical text

No explanation of what the score MEANS ("Below 50 = do not trust", "Above 80 = well-supported")

No colour coding or visual scale to quickly interpret the number

59/100 for a weather question with 0 claims supported is misleadingly high

Recommendation: Add a colour-coded scale (red/amber/green), plain-English interpretation, and recalibrate scoring so off-topic responses score below 20.

Test 7: Navigation / Finding Settings
Rating: 6/10

With sidebar collapsed: icons only, no labels — confusing for new users

With sidebar expanded: clear labels (Chat, Library, Architecture, Reports, Settings)

Settings page is well-organised: LLM Model, Retrieval Settings, Appearance, About section

The gear icon for Settings is industry-standard

Issue: No way to know you can expand the sidebar until you hover over or discover the expand button

Test 8: Report Generation
Rating: 1/10 — CRITICAL FAILURE

Only one report template available: "Product Overview"

Clicked "Generate Report" — button changed to "Generating..." with spinner

After 3+ minutes of loading, the button reverted to "Generate Report"

"Previous Reports (0)" remained unchanged — no report was generated or saved

No error message — another silent failure

Marcus would have no idea if the report generation failed, is still running, or succeeded and went somewhere he can't find

Recommendation: Show progress indication, error messages on failure, and estimated generation time.

Test 9: Architecture View
Rating: 7/10

Clear empty state: "No architecture data yet" with helpful instruction text

"Click 'Extract Architecture' to analyse your imported documents and build a component map showing hardware, interfaces, protocols, and software"

The "Extract Architecture" button is prominent and blue

Minor issues: No explanation of how long extraction takes or what the output looks like. Marcus doesn't know what a "component map" visualization will look like before committing to a potentially long operation.

Test 10: Pinning Facts
Rating: 0/10 — FEATURE MISSING FROM UI

Examined all interactive elements on chat responses — NO pin, bookmark, save, or star button exists

Right-clicking on responses shows only browser context menu, no custom options

The backend API fully supports pinning: Pin Fact, Get Pinned Facts, Unpin Fact, and Suggest Pins endpoints all exist

The feature is implemented server-side but has zero UI exposure

Marcus cannot pin findings through any discoverable interaction

Recommendation: Add a pin icon to each response bubble. Expose the "Suggest Pins" feature as a one-click action.

Cross-Cutting Issues
Issue	Severity	Details
Silent failures	CRITICAL	Queries, vague questions, and report generation all fail without any error message
Extreme latency	HIGH	2-5 minutes per query response; report generation 3+ minutes before silent failure
Duplicate responses	MEDIUM	Responses render twice in the conversation view
No off-topic guard	HIGH	Model fabricates answers to unrelated questions with misleading confidence scores
Empty citations	HIGH	API returns "citations": [] and "sources_used": 0 even when retrieving 10 chunks from 7 documents
No .docx support	MEDIUM	Common document format unsupported
Pinning not in UI	HIGH	Backend feature fully implemented but invisible to users
No onboarding	MEDIUM	New users have no guidance on workflow
Jargon in scores	LOW	Confidence explanations use technical terms without definitions
What Works Well
Project management: Multiple projects with clear naming and document counts

Conversation threading: Conversations are preserved and titled by first query

Confidence scores: Clickable with expanded detail (needs better calibration and plain language)

Architecture page: Clean empty state with clear call-to-action

Settings page: Well-organised with model info, retrieval parameters, and theme toggle

Dark mode: Professional appearance appropriate for security work

Offline architecture: Fully air-gapped operation with local LLM

Verdict
As Marcus, I would report to my team lead: "The tool looks professional but I couldn't get it to work reliably. Most of my questions either failed silently or took several minutes. When I got an answer, it sometimes wasn't related to my documents. I couldn't figure out how to pin findings or generate reports. I'd need significant training and the tool needs bug fixes before I could use it productively."

The SRA v0.1.0 demonstrates a strong architectural vision but is at a prototype stage not suitable for operational use by junior staff. The most critical fixes needed are: (1) error handling with user-visible messages, (2) off-topic query detection, (3) citation extraction actually working, (4) exposing pinning in the UI, and (5) addressing the extreme latency of the Mistral 7B model on available hardware.
Dr. Wei Chen — Technical Precision & Academic Workflow Evaluation
Security Research Assistant v0.1.0 | HMGCC Co-Creation Challenge (CH-2026-001)
Persona: Dr. Wei Chen, visiting security researcher, PhD in embedded systems security, non-native English speaker
Test Date: 13 April 2026
Backend: Mistral 7B (q4_K_M) via Ollama, fully offline
Documents: 50+ Python source files (pytest, ChromaDB components)

Executive Summary
The SRA demonstrates a well-designed backend architecture with a comprehensive REST API surface covering projects, documents, queries, conversations, reports, architecture extraction, user profiles, and data export. However, from the perspective of a precision-focused academic researcher, the tool has fundamental shortcomings: empty citation arrays despite referencing source chunks, a non-functional user preference/adaptation system, response times of 2–9 minutes per query, and a critical disconnect between backend capabilities and frontend exposure. The report generation feature works but takes 12+ minutes and the UI fails to display completed reports.

Overall Assessment: 38/100 — Promising Architecture, Unreliable Execution

Test Results
Test 1: Structured Table Format Request
Rating: 5/10

I requested a Markdown table of all imported modules with columns for module name, function name, parameter types, and return type. The model did produce a Markdown table after approximately 9 minutes:

The response contained proper table headers (| Module Name | Function Name | Parameter Types | Return Type |) and at least one data row referencing coveragepy.io with _get_coverage_data(path: pathlib.Path) returning CoverageData
.

Issues:

Response took ~9 minutes — unacceptable for interactive research

Confidence score of 59/100 is the same score given to a completely off-topic weather question — the scoring system does not differentiate between relevant and irrelevant queries

"citations": [] empty despite the system identifying "10 source chunk(s) from 6 document(s)"

"sources_used": 0 contradicts the confidence explanation mentioning source chunks

The entire response was flagged in flagged_claims — indicating the system has no certainty about its own output

I cannot verify whether the table data is accurate because there are no traceable citations

Test 2: Exact Specification Precision
Rating: 3/10

From analysing all responses returned during testing, the model makes vague generalizations rather than providing exact values. For example, the security vulnerability analysis stated code "does not contain any apparent security vulnerabilities" — a categorical claim without specificity about which code patterns were examined or what vulnerability classes were tested against.

When the model did cite specific function signatures (e.g., allow_untyped_defs(), import_module_or_rewrite_test()), it did not provide parameter types or return annotations. For a researcher who needs IEEE/IEC-level precision about exact voltage ranges, clock frequencies, or register configurations, the tool consistently provides summary-level descriptions rather than specification-level data.

Key concern: The model rounds, approximates, and paraphrases by default. There is no mechanism to enforce precision or to flag when exact values have been substituted with approximations.

Test 3: Cross-Source Comparison
Rating: 3/10

The RAG pipeline retrieves 20 vector results, 20 keyword results, fuses to 20, and reranks to 10. This is a solid retrieval strategy. However, the response format provides no mechanism for side-by-side comparison across sources. When I ask "compare X from document A vs document B", the model produces a narrative paragraph rather than a structured comparison table. There is no explicit cross-referencing feature — the model cannot be directed to pull specific values from named documents and juxtapose them.

Test 4: Mixed-Language Content
Rating: N/A (Could not fully test)

The file upload requires a native browser dialog which cannot be automated. The upload zone accepts "PDF, images, code, text, spreadsheets" but provides no explicit guidance about character encoding support (UTF-8, GB2312, Shift-JIS). For a researcher working with machine-translated Chinese/Japanese datasheets, this is a significant gap:

No mention of encoding handling

No language detection or multi-language indexing capability visible

The vector embedding model (likely all-MiniLM-L6 or similar) may not handle CJK characters well

Test 5: Standards Reference Handling
Rating: 2/10

Based on observed behaviour with off-topic queries, asking about "IEC 61131 compliance features" when the documents contain Python code (not PLC specifications) would likely produce a hallucinated response. The system demonstrated with the weather query that it will fabricate answers rather than stating "this information is not present in your documents". It even suggested using external APIs on what should be an air-gapped system.

The model has no concept of standards databases or normative reference handling. It cannot map a standard number (e.g., IEC 62443) to a compliance framework.

Test 6: Report Generation & Precision
Rating: 6/10

The report generation feature works and produces a well-structured document with 8 sections:

Executive Summary

Product Identification

System Architecture Overview

Component Inventory

Interface Map (with Markdown table)

Source Library Summary

Information Gaps

Appendix: Source Documents

Strengths:

Correctly identified ChromaDB as the primary product

Interface Map section includes a structured table with Module/Class, Interface, Purpose, Protocol columns

Information Gaps section explicitly calls out what's unknown — good academic practice

Source Library Summary lists 374 documents with tier classification

Inline citations reference specific files: [Source: AsyncCollection.py, General]

Weaknesses:

Generation took 757.9 seconds (12.6 minutes) with 8 LLM calls

The UI displayed "Previous Reports (0)" even after the report completed — the frontend never showed the completed report

All "citations" arrays are empty [] — the structured citation system is non-functional

confidence_note is null for all 8 sections

Specifications are descriptive, not exact (e.g., "manages embeddings, metadata, and documents" rather than listing specific API parameters)

No version numbers, dependency versions, or quantitative metrics in the report

Test 7: JSON Export & Machine-Readability
Rating: 7/10

The REST API provides well-structured JSON across all endpoints:

Available export mechanisms:

GET /api/v1/conversations/{id} — full conversation with messages, citations, confidence scores

GET /api/v1/reports/{id} — complete report with sections, metadata

GET /api/v1/reports/{id}/export — dedicated export endpoint

GET /api/v1/profile/export — profile and preferences export

POST /api/v1/maintenance/export — full data export

Strengths:

Clean JSON structure with proper field names

Pagination on conversation lists (total, limit, offset)

Timestamps in ISO 8601 format

Report metadata includes generation_time_seconds, llm_calls, sources_used

Weaknesses:

No export button in the UI — a researcher must use the API directly or browser developer tools

citations array is always empty, making the structured JSON unreliable for automated processing

Confidence explanations are embedded as text strings rather than structured fields (e.g., "Based on 10 source chunk(s) from 7 document(s)" should be {"source_chunks": 10, "documents": 7})

No batch export for multiple conversations

sources_used: 0 contradicts the confidence text consistently

Test 8: Follow-up Conversation Chain
Rating: 5/10

The conversation system maintains context across messages. Each conversation gets a unique UUID and is linked to a project. Messages include role (user/assistant), timestamps, and confidence scores. The sidebar correctly lists all conversations with truncated titles.

Issues:

Conversation summaries are all null — the Force Summarise API endpoint exists but summaries are never auto-generated

No mechanism to fork conversations or branch from a specific message

The follow-up chain depends entirely on Mistral 7B's context window (4096 tokens from settings), which is severely limiting for multi-turn technical analysis

With 512 token chunks and 10 retrieved chunks, the context is mostly consumed by RAG context, leaving minimal room for conversation history

Test 9: Numbered List / Format Compliance
Rating: 5/10

The model partially follows format instructions. When asked for a Markdown table, it produced one (Test 1). When asked about modules, it produced numbered lists with bullet points. However:

Format compliance is inconsistent — sometimes numbered, sometimes bulleted

No user-configurable output format preference in the UI

The format_preference field in the profile API is set to "mixed" but has no UI control

No way to set a session-wide preference like "always use tables" or "always use numbered lists"

Test 10: Preference Adaptation & Learning
Rating: 1/10 — NON-FUNCTIONAL

The profile system exists in the API but is entirely non-functional:

query_count: 0 despite 5+ queries executed

first_query_at: null and last_query_at: null despite active use

topic_frequencies: {} despite repeated code analysis queries

frequent_topics: [] empty

detail_preference: 0.5 never changes

format_preference: "mixed" — no mechanism to update from the UI

custom_preferences: {} always empty

The Update Preferences API endpoint (PUT /api/v1/profile/preferences) exists but the frontend has no UI for it. The system does not adapt to user behaviour — every interaction is treated as a first interaction.

Cross-Cutting Technical Issues
Issue	Severity	Impact on Academic Workflow
Empty citation arrays	CRITICAL	Cannot trace claims to source documents; unacceptable for formal reporting
sources_used always 0	CRITICAL	Contradicts confidence text; suggests citation pipeline is disconnected
9-minute query response	CRITICAL	Renders interactive analysis impossible; 5 queries = 45 minutes of waiting
12.6-minute report generation	HIGH	Unusable for iterative report refinement
Profile system non-functional	HIGH	No preference adaptation or usage tracking
No UI for report viewing	HIGH	Reports generated but invisible in frontend
No UI for JSON export	MEDIUM	Researchers must use API directly
No cross-reference mode	MEDIUM	Cannot compare values across specific documents
No encoding documentation	MEDIUM	Unclear CJK character support for multilingual docs
4096 max context tokens	MEDIUM	Limits multi-turn conversation depth
Confidence score miscalibration	HIGH	59/100 for both relevant tables and off-topic weather — meaningless scoring
What the Architecture Gets Right
Comprehensive API design: The REST API covers projects, documents, queries, conversations, reports, architecture, profiles, and maintenance — a complete research workflow

Hybrid retrieval: Vector search + keyword search → fusion → reranking is a sound RAG pipeline

Source tiering concept: Manufacturer, Academic, Trusted Forum, Unverified classification is appropriate for security research

Report sections: The 8-section report template mirrors standard security assessment structure

Offline-first design: Fully air-gapped with local LLM and vector store — correct for classified environments

Pinning API: Pin Fact, Get Pinned Facts, Suggest Pins endpoints show good design intent

Architecture extraction concept: Automated component mapping from documents is a valuable feature for ICS assessment

Verdict
As Dr. Chen, I would report to my home institution: "The Security Research Assistant demonstrates a thoughtful architectural design with a comprehensive API surface that covers the complete assessment workflow. However, the implementation has critical gaps that prevent academic use: citations are never populated despite claims of source grounding, response times of 2–12 minutes make interactive research impossible, the user preference system is non-functional, and there is a significant disconnect between backend capabilities and frontend exposure. The report generation feature works but is invisible in the UI. I would recommend this tool for continued development with emphasis on: (1) fixing the citation pipeline, (2) upgrading to a faster model or adding GPU acceleration, (3) exposing existing backend features (pinning, preferences, export) in the frontend, and (4) adding cross-reference comparison and precision-mode capabilities for technical specification analysis."

The tool is architecturally sound but operationally premature for precision research. It would benefit greatly from a researcher-in-the-loop development sprint to close the gap between its API capabilities and user-facing functionality.

Here is my systematic evaluation of the Security Research Assistant (SRA) v0.1.0 against the CH-2026-001 Essential Requirements, based on direct observation of all five application sections.

Evaluation Overview
The SRA is a locally-hosted web application (localhost:1420) running Ollama with mistral:7b-instruct-v0.3-q4_K_M for inference and nomic-embed-text:latest for embeddings, with 5,170+ documents indexed. It presents five main sections: Chat, Library, Architecture, Reports, and Settings. Below is the requirement-by-requirement assessment.

ER-01: Architecture Extraction
Test: Import datasheets → extract architecture → view component map
Expected: Components, interfaces, protocols identified

Result: PARTIAL PASS — UI present, output unverifiable

The Architecture page exists with an "Extract Architecture" button and promises to "analyse your imported documents and build a component map showing hardware, interfaces, protocols, and software". However, it currently shows "No architecture data yet." The 50 documents currently in the Library are Python source files (Pygments themes, PIL plugins), not industrial datasheets or hardware manuals. Without representative ICS documentation loaded, the extraction pipeline cannot be meaningfully evaluated. Blocker: No test data matching the additive manufacturing use case is pre-loaded.

ER-02: Citation & Unsourced Claim Flagging
Test: Ask a question, deliberately look for unsourced claims
Expected: Every claim cited or flagged

Result: PASS — with minor formatting issues

The existing chat response demonstrates inline citations ([Source: SpiderImagePlugin.py, Page None], [Source: File Comments]) and a dedicated "Flagged claims" section that explicitly calls out assertions "not found in the retrieved source material". The system identified that only 2 of 5 claims were supported by sources and flagged the remaining 3. This is a strong implementation. Minor issue: One source shows [Source: unknown, Page 0] — the "unknown" source name is unhelpful for a researcher verifying provenance.

ER-03: Multi-Format Document Import
Test: Import PDF, image, code, text, CSV — all indexed
Expected: All types parse successfully

Result: PARTIAL PASS — 2 of 5 types verified

The Library page advertises support for "PDF, images, code, text, spreadsheets" and provides corresponding type filters. The upload interface includes drag-and-drop and source-quality tagging (Manufacturer, Academic, Trusted Forum, Unverified). Currently, 50 documents are loaded, all appearing to be code (.py, .h) and text (.txt) files. Cannot verify PDF parsing, image OCR/analysis, or spreadsheet handling from available evidence. The filter dropdowns exist but may be aspirational rather than functional.

ER-04: Source Tier Badges
Test: Check source tier badges on citations
Expected: Tiers displayed, Tier 1 weighted higher

Result: PARTIAL PASS — tiers displayed, weighting unverifiable

Four tiers are implemented: Manufacturer, Academic, Trusted Forum, Unverified. The Library allows tier assignment at upload time, and the Chat confidence breakdown shows tier composition: "Source tiers: Unverified / General Source: 10". However, all 50 current documents are tagged "Unverified," making it impossible to test whether Tier 1 (Manufacturer) sources are genuinely weighted higher in retrieval and confidence scoring. This is a critical gap in test evidence.

ER-05: Confidence Score Differentiation
Test: Ask well-sourced and poorly-sourced questions
Expected: Confidence scores differ appropriately

Result: INCONCLUSIVE — only one data point

The single observed response shows confidence 67/100 with the breakdown "2/5 claims supported by sources". The confidence mechanism exists and produces a numeric score. However, with only one conversation visible, I cannot verify that well-sourced questions produce meaningfully higher scores. Need at least two queries with different source coverage to validate differential scoring.

ER-06: Offline Operation
Test: Check health endpoint, verify no external calls
Expected: status: ok, zero network egress

Result: PASS (observational)

Indicator	Evidence
LLM	Local Ollama (mistral:7b-instruct-v0.3-q4_K_M) 
Embeddings	Local (nomic-embed-text:latest) 
Health status	"All systems OK (5170 docs)" in notification bar 
Offline claim	"Fully offline operation — no internet required" 
Hosting	localhost:1420 — no external API endpoints observed 
Caveat: Full verification requires network traffic analysis (e.g., Wireshark capture during operation). No external CDN assets, analytics beacons, or telemetry endpoints were observed in the page content.

ER-07: Natural Language Q&A
Test: Ask natural language question, get conversational answer
Expected: Cited, structured, relevant

Result: PASS

The chat response to "What are the main image processing libraries and modules used in this codebase?" is conversational, structured with numbered bullets, includes inline source citations, and is relevant to the indexed documents. The response also includes the confidence score and flagged claims — exceeding the basic requirement.

ER-08: Conversation Persistence
Test: Have 5-message conversation, close, reopen
Expected: Context preserved

Result: NOT FULLY TESTABLE

The chat shows one previous conversation that persisted across page navigation (it was still visible when I loaded the Chat page). The Reports page shows "Previous Reports (2)" with timestamps, confirming some persistence. However, I cannot verify 5-message thread persistence or session recovery without performing a full multi-turn test.

Scoring Summary
Requirement	Status	Score (1-5)	Blocker?
Requirement	Status	Score (1-5)	Blocker?
ER-01 Architecture extraction	Partial Pass	3	No test data
ER-02 Citation/flagging	Pass	4	Minor (unknown source)
ER-03 Multi-format import	Partial Pass	3	Only code/text verified
ER-04 Source tier badges	Partial Pass	3	No multi-tier test data
ER-05 Confidence differentiation	Inconclusive	2	Single data point
ER-06 Offline operation	Pass	5	None
ER-07 Natural language Q&A	Pass	4	None
ER-08 Conversation persistence	Not fully tested	3	Needs multi-turn test
Key Findings for Challenge Panel
Strengths: The offline architecture is genuinely air-gapped with local Ollama, the citation-and-flagging system (ER-02) is the standout feature, and the report export options (Markdown/PDF/JSON/HTML) show operational maturity.

Critical gaps: The demo environment is loaded with Python library source code rather than representative ICS/additive manufacturing documentation, which makes it impossible to properly evaluate ER-01, ER-04, and ER-05 in a "relevant environment" — a requirement for TRL-6. The mistral:7b model is lightweight but may struggle with complex technical reasoning on real hardware datasheets. I would recommend re-testing with a curated document set matching the additive manufacturing assessment use case before final scoring.

SRA Test Execution Report — Alicia's 11-Phase Test Script
Tester: Alicia (Senior Security Researcher persona)
Date: 2026-04-13
System: SRA v0.1.0, Mistral 7B Q4_K_M, ChromaDB
Project: "Additive Manufacturing Assessment" (4790 documents indexed — Python library files from .venv)

Phase 1: Document Import & Source Tagging (Tests 1–2)
Test 1: Document Import ✅ PASS (with issues)
Library page displays documents with filename, size, date, source tier badge, and processing status

Grid/List view toggle, search, type filter, tier filter, sort all present

BUG P2: Pagination shows "Showing 50 of 50 documents" when API reports 4665+ total — should show "Showing 50 of 4665"

BUG P3: Some documents show spinning indicator (still processing) even days after import

Test 2: Source Tier Tagging ✅ PASS (with bug)
Four source tiers available: Manufacturer, Academic, Trusted Forum, Unverified

Tier changing via UI buttons on document detail page works — backend correctly updates

BUG P2: Badge at top of document detail page does NOT update after tier change — shows stale "Unverified" even when backend confirms tier_1_manufacturer

Phase 1 Score: 4/6 (Import works but pagination misleading; tier change works but badge stale)

Phase 2: Query & Citation Accuracy (Tests 3–5)
Test 3: Specific Factual Query ✅ PARTIAL PASS
Query: "What are the main image processing libraries and modules used in this codebase?"

Response time: ~120 seconds (very slow for a simple query)

Answer correctly identifies TIFF, Spider Image Format, and PIL

Citations provided with document_id, chunk_id, relevance_score, excerpt

Inline [Source: filename, Page X] references in answer text

BUG P1: document_name: "unknown" for one citation — name resolution failure

BUG P2: Duplicate citations — same chunk_id appears twice with different document_name

BUG P3: Very low relevance scores (0.016) suggesting poor retrieval quality

Test 4: Multi-Source Synthesis — TESTED via security query
Query: "What are the security vulnerabilities in the imported code?"

Answer synthesizes from 9 documents, identifies 5 security concern categories

Response time: ~210 seconds

Test 5: Uncertainty Flagging ✅ PASS
Confidence score: 59/100 with clear explanation

"0/2 claims supported by sources" — excellent honesty about lack of evidence

2 claims flagged as "technical assertions not found in the retrieved source material"

BUG P2: Confidence explanation says "10 source chunks from 9 documents" but citations: [] is empty — inconsistency between metadata and citations array

BUG P3: Confidence score displayed redundantly: "Confidence: 59/100 — Confidence: 59/100" (doubled text)

Phase 2 Score: 6/9 (Citations work but have bugs; uncertainty flagging excellent; response time very slow)

Phase 3: Findings Management (Tests 6–7)
Test 6: Pin Key Findings ❌ FAIL
CRITICAL BUG P1: No pin button exists in the Chat UI — pinning is only possible via API

Swagger UI "Try it out" → "Execute" for the Pin Fact endpoint did NOT execute the request (no server response section appeared)

Pin API endpoint GET /pins returns empty even after attempted pin via Swagger

The feature exists in the backend but is completely inaccessible from the frontend

Test 7: Suggest Pins — NOT TESTABLE
Depends on working pin functionality

API endpoint exists (/suggest-pins) but untestable without working pins

Phase 3 Score: 0/6 (Pin feature not accessible from UI; API execution failed)

Phase 4: Multi-thread Context (Tests 8–9)
Test 8: Create Second Conversation ✅ PASS
Conversation list visible in expanded sidebar

7 conversations displayed with truncated titles

"+" button available to create new conversations

Each conversation loads correctly when clicked

Test 9: Context Preservation ✅ PASS (with issues)
Returning to first conversation correctly loads previous messages and response

Conversation title, messages, citations, confidence score all preserved

BUG P2: Project selector resets to "Select Project" when navigating to Chat — must re-select project

BUG P3: Chat input field submission via UI failed silently (first attempt) — no error message shown, no conversation created

Phase 4 Score: 4/6 (Conversations work but silent failures and project selector reset)

Phase 5: Report Generation (Tests 10–11)
Test 10: Generate Product Overview Report ✅ PASS (with caveats)
Previous report found: generation took 757.9 seconds (12.6 minutes), 8 LLM calls, 374 sources

Report contains structured sections: "Executive Summary", "Product Identification"

Content includes inline source citations and uncertainty flags ("Source: Not Available")

4 report types available: Product Overview, Component Analysis, System Architecture, Investigation Summary

4 export formats: MARKDOWN, PDF, JSON, HTML

New report generation was still running after 2.5+ minutes (expected given prior 12.6min result)

Test 11: Report Quality — PARTIAL PASS
Report correctly identifies ChromaDB as the primary product from the imported code

Sections are structured and sourced

BUG P3: Report content is about Python library internals (ChromaDB, PIL) rather than any real product — but this is expected given the imported documents were .venv files, not proper test documents

Phase 5 Score: 4/6 (Reports generate successfully with citations; very slow; export options present)

Additional Findings
Settings Page Bugs
BUG P1: "Ollama status: Disconnected" and "No models available" despite health endpoint confirming Ollama is connected with mistral:7b-instruct available

BUG P2: "Documents indexed: —" shows dash instead of actual count (should show 4790)

Architecture Page
Page loads correctly with "Extract Architecture" button and empty state message

Not tested for extraction (would require additional LLM processing time)

UI/UX Issues
BUG P2: Chat input "Ask a question about your documents" failed silently — no error feedback when query fails

BUG P3: Sidebar must be manually expanded to see conversations — no conversation list in collapsed view

PERFORMANCE: Query response times of 120-210 seconds are unacceptable for interactive research

Scoring Rubric Summary (33 Points)
Phase	Test	Max	Score	Notes
1	T1: Document Import	3	2	Pagination display bug
1	T2: Source Tagging	3	2	Badge doesn't update
2	T3: Factual Query	3	2	Unknown doc name, duplicates
2	T4: Multi-source	3	2	Works but empty citations array
2	T5: Uncertainty	3	3	Excellent flagging
3	T6: Pin Findings	3	0	No UI, API failed
3	T7: Suggest Pins	3	0	Untestable
4	T8: New Conversation	3	3	Works correctly
4	T9: Context Preserved	3	2	Project selector resets
5	T10: Generate Report	3	2	Extremely slow (12+ min)
5	T11: Report Quality	3	2	Structured but based on wrong docs
TOTAL		33	20	60.6%
Critical Bug Summary (Priority Ranked)
P1-CRITICAL: Pin functionality missing from Chat UI entirely

P1-CRITICAL: Settings shows Ollama "Disconnected" when it's actually connected

P2-HIGH: Document tier badge doesn't refresh after tier change

P2-HIGH: Citation document_name resolves to "unknown"

P2-HIGH: Duplicate citations with same chunk_id

P2-HIGH: Empty citations array despite confidence metadata citing sources

P2-HIGH: Chat query submission fails silently (no error feedback)

P2-HIGH: Project selector resets when navigating between views

P2-HIGH: Pagination count misleading (50 of 50 vs actual 4665)

P3-MEDIUM: Confidence text duplicated in response

P3-MEDIUM: Documents indexed count shows "—" in Settings

PERFORMANCE: Query response 120-210s; Report generation 12+ minutes
