# Security Review — SRA v0.1.0

## Review Date
2026-04-12

## 1. Network Isolation

**Finding: PASS** — No external network calls detected.

All HTTP calls in Python target `localhost` only:
- `ollama` library connects to `http://localhost:11434`
- `urllib.request` in launcher checks `localhost:11434` and `localhost:8000`
- No use of `requests`, `httpx`, or external URL calls in production code

All `fetch()` calls in TypeScript target `http://localhost:8000/api/v1`.

## 2. Secrets and Credentials

**Finding: PASS** — No hardcoded secrets found.

- No API keys, tokens, or passwords in source code
- `.env` file is gitignored; only `.env.example` with placeholder values is committed
- All configuration uses environment variables with sensible defaults

## 3. SQL Injection

**Finding: PASS** — All SQL queries use parameterised queries.

All SQLite operations use `?` placeholder parameterisation via `sqlite3` module.
No string-formatted SQL statements found in production code.

## 4. Path Traversal

**Finding: PASS with NOTE**

Uploaded files are stored in `data/uploads/{project_id}/{filename}`. The filename
comes from the user upload. Recommendation for hardening: sanitise filenames to
remove `..` and special characters before storage. Current risk is low as the
application runs locally with user-level permissions.

## 5. File Size Limits

**Finding: PASS** — PDF parser enforces 500MB limit. Upload endpoint relies on
server memory limits. Recommendation: add explicit `max_upload_size` to FastAPI.

## 6. Classification Markings

**Finding: IMPLEMENTED** — PDF reports include "OFFICIAL" marking on cover page.
Classification level should be made configurable via `config.yaml` for use at
higher classification levels.

## 7. Data at Rest

**Finding: NOTE** — SQLite and ChromaDB store data unencrypted on disk.
For classified environments, recommend using OS-level disk encryption
(BitLocker on Windows, LUKS on Linux).

## 8. Dependency Review

All dependencies are open-source with permissive licences (MIT, Apache 2.0, BSD).
No dependencies phone home or require network access for functionality.
Key dependencies: FastAPI, ChromaDB, Ollama, PyMuPDF, Tesseract, tree-sitter.

## 9. Recommendations

1. Add filename sanitisation on upload
2. Configure explicit upload size limit in FastAPI
3. Make classification level configurable
4. Consider SQLite encryption (SQLCipher) for higher classification levels
5. Add audit logging for all data access operations
