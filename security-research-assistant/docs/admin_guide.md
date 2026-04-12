# Security Research Assistant — Administrator Guide

## 1. Deployment Architecture

The SRA consists of three local services:
- **Frontend:** Tauri desktop application (React + TypeScript)
- **Backend:** Python FastAPI server on `localhost:8000`
- **LLM:** Ollama server on `localhost:11434`

All communication is localhost-only. Zero network egress.

## 2. Security Considerations

- All data stored locally in `data/` directory
- SQLite database at `data/sqlite/sra.db`
- Vector embeddings at `data/vectordb/`
- No telemetry, no analytics, no external calls
- Suitable for OFFICIAL classification environments
- Consider file system encryption for data-at-rest protection

## 3. Configuration Reference

### Environment Variables (SRA_ prefix)
| Variable | Default | Description |
|----------|---------|-------------|
| SRA_OLLAMA_BASE_URL | http://localhost:11434 | Ollama server URL |
| SRA_OLLAMA_MODEL | mistral:7b-instruct-v0.3-q4_K_M | LLM model name |
| SRA_OLLAMA_EMBED_MODEL | nomic-embed-text | Embedding model |
| SRA_CHROMA_PATH | ./data/vectordb | ChromaDB storage |
| SRA_SQLITE_PATH | ./data/sqlite/sra.db | SQLite database |
| SRA_LOG_LEVEL | INFO | Logging level |
| SRA_CHUNK_SIZE | 512 | Document chunk size (tokens) |
| SRA_TOP_K | 10 | Number of search results |
| SRA_MAX_CONTEXT_TOKENS | 4096 | LLM context window budget |

### config.yaml
Placed in the application root. Environment variables override YAML values.

## 4. Maintenance

### Backup
```bash
python scripts/update.py export --output backup.sra-backup
```

### Restore
```bash
python scripts/update.py import --input backup.sra-backup
```

### Model Update (Air-Gapped)
1. On a connected machine: `ollama pull <new-model>`
2. Copy model files to USB
3. On air-gapped machine: `ollama create <name> -f <modelfile>`
4. Update SRA_OLLAMA_MODEL in config

### Database Maintenance
```sql
-- Integrity check
PRAGMA integrity_check;

-- Vacuum to reclaim space
VACUUM;
```

## 5. Performance Tuning

| Parameter | Effect | Recommendation |
|-----------|--------|----------------|
| SRA_TOP_K | More results = better coverage, slower | 5-15 for most use cases |
| SRA_CHUNK_SIZE | Larger = more context per chunk | 256-1024 tokens |
| SRA_MAX_CONTEXT_TOKENS | Larger = more context for LLM | Match your model's window |
| Model quantisation | Q4 = fastest, Q8 = best quality | Q4_K_M for CPU, Q5+ for GPU |

### Hardware Recommendations
- **Minimum:** 8 GB RAM, 4-core CPU, 20 GB disk
- **Recommended:** 16 GB RAM, 8-core CPU, SSD, 50 GB disk
- **Optimal:** 32 GB RAM, NVIDIA GPU (RTX 3060+), NVMe SSD

## 6. API Documentation

The backend auto-generates OpenAPI documentation at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json
