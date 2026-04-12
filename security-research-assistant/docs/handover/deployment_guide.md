# Deployment Guide — HMGCC Testing

## Pre-requisites

- [ ] Target machine: Windows 10/11 x64 or Linux x64
- [ ] 16 GB RAM (8 GB minimum)
- [ ] 20 GB free disk space
- [ ] Python 3.11+ installed (3.11-3.13 recommended for full PDF support)
- [ ] Node.js 20+ installed (for frontend development only)
- [ ] Ollama installed (https://ollama.com)

## Step-by-Step Installation

### 1. Install Ollama and Models
```bash
# Install Ollama (follow platform-specific instructions from ollama.com)
# Then pull required models:
ollama pull mistral:7b-instruct-v0.3-q4_K_M
ollama pull nomic-embed-text
```

### 2. Install Python Backend
```bash
cd security-research-assistant
pip install -e ".[dev]"
```

### 3. Start Services
```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start backend
cd security-research-assistant
uvicorn backend.main:app --host 127.0.0.1 --port 8000

# Terminal 3: Start frontend (development mode)
cd security-research-assistant/frontend
npm install
npm run dev
```

### 4. Verify Installation
Navigate to `http://localhost:8000/api/v1/health` — should return:
```json
{"status": "ok", "ollama_connected": true, "database_ok": true, "vector_store_ok": true}
```

### 5. Load Test Data
HMGCC will provide their own test data. Import via:
- Drag-and-drop onto the Library page in the UI
- Or via API: `POST http://localhost:8000/api/v1/documents/upload`

## Configuration

Edit `config.yaml` or set environment variables (SRA_ prefix) to customise:
- LLM model selection
- Chunk size and retrieval parameters
- Log level and data paths

See `docs/admin_guide.md` for full configuration reference.

## Troubleshooting

| Issue | Check |
|-------|-------|
| Backend won't start | Is port 8000 free? Is Python installed? |
| Ollama not connecting | Is `ollama serve` running? Is port 11434 free? |
| No model available | Run `ollama pull mistral:7b-instruct-v0.3-q4_K_M` |
| Slow responses | Check RAM usage, consider GPU |
| Import failures | Check file format is supported, file is not corrupted |
