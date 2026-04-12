# Performance Report — SRA v0.1.0

## Test Environment
- **Build:** Development environment (not production-packaged)
- **Python:** 3.14.3
- **Ollama model:** Requires mistral:7b-instruct-v0.3-q4_K_M (not installed during build)
- **Test dataset:** Sample project fixtures (5 documents)

## Unit Test Performance
| Metric | Value |
|--------|-------|
| Total tests | 234 |
| Passed | 234 |
| Skipped | 11 (Python 3.14 html.entities) |
| Failed | 0 |
| Total time | ~5 seconds |

## Frontend Build Performance
| Metric | Value |
|--------|-------|
| TypeScript compilation | Clean (0 errors) |
| Vite production build | ~6 seconds |
| Bundle size (JS) | 498 KB (150 KB gzipped) |
| Bundle size (CSS) | 45 KB (8 KB gzipped) |

## Ingestion Performance (Estimated)
| Document Type | Parse Time | Chunk Time | Total per Doc |
|---------------|-----------|------------|---------------|
| PDF (10 pages) | ~2s | ~0.5s | ~3s + embedding |
| Image (OCR) | ~3s | ~0.2s | ~4s + embedding |
| Code (500 lines) | ~0.5s | ~0.3s | ~1s + embedding |
| Text (1000 words) | ~0.1s | ~0.2s | ~0.5s + embedding |
| CSV (100 rows) | ~0.1s | ~0.1s | ~0.3s + embedding |

*Note: Embedding time depends on Ollama model and hardware (~0.5-2s per batch of 50 chunks)*

## Query Performance (Estimated)
| Component | Estimated Time |
|-----------|---------------|
| Vector search (ChromaDB) | 10-50ms |
| BM25 keyword search | 5-20ms |
| RRF fusion | <5ms |
| LLM re-ranking | 2-5s (if enabled) |
| Context building | <10ms |
| LLM generation | 5-30s (CPU), 1-5s (GPU) |
| Validation pipeline | <100ms |
| **Total (CPU, no rerank)** | **5-30s** |
| **Total (GPU, no rerank)** | **1-5s** |

## Resource Usage (Estimated)
| Metric | At Rest | During Query |
|--------|---------|-------------|
| Backend memory | ~150 MB | ~300 MB |
| ChromaDB memory | ~50 MB | ~100 MB |
| Ollama memory | ~4 GB (model loaded) | ~5 GB |

## Disk Usage
| Component | Per 100 Documents |
|-----------|-------------------|
| SQLite (metadata + chunks) | ~10-50 MB |
| ChromaDB (embeddings) | ~50-200 MB |
| Uploaded files (copies) | Varies by document size |

## Recommendations
- **Minimum hardware:** 8 GB RAM, 4-core CPU, 20 GB free disk, SSD recommended
- **Recommended:** 16 GB RAM, 8-core CPU, NVIDIA GPU (6 GB+ VRAM), NVMe SSD
- **For 1000+ documents:** Consider increasing SRA_TOP_K gradually, monitor memory
- **For faster responses:** Use GPU acceleration, or a smaller quantised model (Q3)
