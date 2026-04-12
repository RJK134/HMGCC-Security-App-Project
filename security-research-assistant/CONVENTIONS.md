# Coding Conventions

## Python (Backend + Core)
- Python 3.11+ required
- Type hints on all function signatures
- Pydantic models for all API request/response schemas
- `logging` module for structured logging (no print statements)
- Docstrings on public functions and classes (Google style)
- Config via YAML or environment variables — never hardcoded paths
- No network calls — enforce offline operation at every layer
- `pytest` for testing with fixtures in `tests/fixtures/`

## Naming
- Files and directories: `snake_case`
- Classes: `PascalCase`
- Functions and variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- API routes: `/api/v1/resource_name`

## Project Organisation
- Core logic in `core/` — each module is self-contained with its own models and utils
- API route handlers in `backend/api/` — thin layer delegating to core
- Config in `backend/config.py` — single source of truth for all settings
- Tests mirror source structure: `tests/test_ingest/` tests `core/ingest/`

## Frontend (TypeScript + React)
- TypeScript strict mode
- Functional components with hooks
- CSS modules or Tailwind
- Components in `frontend/src/components/`
- API client in `frontend/src/api/`

## Git
- Conventional commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`
- Feature branches off `main`
- No secrets or data files committed

## Error Handling
- Validate at system boundaries (API inputs, file imports)
- Structured error responses from API (JSON with error code and message)
- Graceful degradation on parse failures (log warning, skip bad chunk, continue)
