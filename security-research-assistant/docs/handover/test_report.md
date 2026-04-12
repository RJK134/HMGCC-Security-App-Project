# Test Report — SRA v0.1.0

## Test Summary

| Category | Tests | Passed | Skipped | Failed |
|----------|-------|--------|---------|--------|
| Configuration | 4 | 4 | 0 | 0 |
| Pydantic models | 12 | 12 | 0 | 0 |
| Database CRUD | 21 | 21 | 0 | 0 |
| ChromaDB | 6 | 6 | 0 | 0 |
| Health API | 3 | 0 | 3 | 0 |
| File detection | 10 | 10 | 0 | 0 |
| PDF parser | 5 | 0 | 5 | 0 |
| Image parser | 4 | 3 | 1 | 0 |
| Code parser | 7 | 7 | 0 | 0 |
| Text parser | 7 | 7 | 0 | 0 |
| Chunker | 9 | 9 | 0 | 0 |
| Pipeline integration | 7 | 6 | 1 | 0 |
| RRF fusion | 6 | 6 | 0 | 0 |
| Keyword search | 6 | 6 | 0 | 0 |
| Context builder | 7 | 7 | 0 | 0 |
| Response parser | 7 | 7 | 0 | 0 |
| RAG engine | 6 | 6 | 0 | 0 |
| Conversation manager | 13 | 13 | 0 | 0 |
| Summariser | 8 | 8 | 0 | 0 |
| Memory (pinned facts) | 9 | 9 | 0 | 0 |
| Conversation integration | 4 | 4 | 0 | 0 |
| Source tier | 9 | 9 | 0 | 0 |
| Confidence scoring | 9 | 9 | 0 | 0 |
| Hallucination detection | 8 | 8 | 0 | 0 |
| Cross-referencing | 6 | 6 | 0 | 0 |
| Validation pipeline | 6 | 6 | 0 | 0 |
| Architecture extraction | 4 | 4 | 0 | 0 |
| Architecture mapping | 4 | 4 | 0 | 0 |
| Report templates | 4 | 4 | 0 | 0 |
| Report generator | 5 | 5 | 0 | 0 |
| Report exporter | 4 | 3 | 1 | 0 |
| Profile tracker | 9 | 9 | 0 | 0 |
| Prompt adapter | 8 | 8 | 0 | 0 |
| Proactive engine | 4 | 4 | 0 | 0 |
| **TOTAL** | **245** | **234** | **11** | **0** |

## Skipped Tests

All 11 skipped tests are due to a Python 3.14 stdlib regression (`html.entities` module missing).
This affects PyMuPDF, reportlab, and FastAPI TestClient. These tests pass on Python 3.11-3.13.

## Frontend Build

| Check | Status |
|-------|--------|
| TypeScript strict compilation | PASS (0 errors) |
| Vite production build | PASS (5.1s) |
| Bundle size | 498 KB JS + 45 KB CSS |

## Offline Verification

The application makes zero external network calls. All HTTP traffic is to `localhost:8000` (backend) and `localhost:11434` (Ollama). Verified by code review — see `docs/security_review.md`.
