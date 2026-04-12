# Security Research Assistant — User Guide

## 1. Introduction

The Security Research Assistant (SRA) helps security researchers characterise complex industrial machinery by indexing, searching, and querying technical documentation using local AI. It runs entirely on your laptop — no internet connection required.

### Key Capabilities
- **Import** technical documents: PDFs, datasheets, schematics, source code, images, spreadsheets
- **Ask** natural-language questions and receive cited, confidence-scored answers
- **Validate** every response against source material to prevent hallucination
- **Remember** conversation context across sessions spanning weeks
- **Map** system architecture: components, interfaces, protocols
- **Generate** professional reports (PDF, Markdown, JSON, HTML)

### Privacy and Security
All data stays on your machine. No telemetry. No cloud APIs. Suitable for OFFICIAL classification environments.

## 2. Installation

### System Requirements
- **OS:** Windows 10/11 (x64) or Linux (x64, Ubuntu 20.04+)
- **RAM:** 16 GB recommended (8 GB minimum)
- **Disk:** 20 GB free (including LLM models)
- **Optional:** NVIDIA GPU with 6 GB+ VRAM for faster inference

### Steps
1. Extract the installation archive to your preferred location
2. Install Ollama (if not already present)
3. Pull the required models: `ollama pull mistral:7b-instruct-v0.3-q4_K_M` and `ollama pull nomic-embed-text`
4. Run the launcher: `python launcher.py`
5. The application will open automatically

## 3. Getting Started

On first launch, a setup wizard guides you through:
1. **System check** — verifies all services are running
2. **Project creation** — create your first investigation project
3. **Document import** — drag files into the Library

## 4. Importing Documents

### Supported File Types
| Type | Extensions | Best For |
|------|-----------|----------|
| PDF | .pdf | Datasheets, manuals, specifications |
| Images | .png, .jpg, .tiff | Circuit boards, schematics, annotations |
| Code | .c, .h, .py, .asm | Firmware, source code, scripts |
| Text | .txt, .md, .html | Notes, forum posts, documentation |
| Spreadsheets | .csv, .xlsx | Component inventories, specifications |

### Source Quality Tiers
Assign a quality tier when importing to improve confidence scoring:
- **Tier 1 — Manufacturer:** Official datasheets and manuals (highest trust)
- **Tier 2 — Academic:** IEEE/IEC standards, peer-reviewed papers
- **Tier 3 — Trusted Forum:** Stack Overflow, expert blogs
- **Tier 4 — Unverified:** Unknown sources (default)

## 5. Asking Questions

Type natural-language questions in the Chat interface. The tool searches your imported documents, assembles relevant context, and generates a grounded answer.

### Understanding Responses
- **Citations** — Clickable badges showing which document and page was used
- **Confidence Score** — 0-100 rating based on source quality and coverage
- **Flagged Claims** — Warnings for statements that couldn't be verified
- **Alternative Interpretations** — Shown when sources disagree

### Tips for Better Results
- Be specific: "What is the clock speed of the STM32F407?" rather than "Tell me about the processor"
- Import more source documents to improve answer quality
- Pin key findings to preserve them across sessions

## 6. Managing Conversations

- Create multiple conversation threads per project
- Resume conversations weeks later — context is automatically reconstructed
- Pin important discoveries as key facts (always included in future queries)

## 7. Architecture Analysis

Click "Extract Architecture" to analyse your documents and build a component map showing:
- Hardware components (processors, memory, sensors)
- Communication interfaces (SPI, I2C, UART)
- Protocols (Modbus, OPC-UA)
- Software stack

## 8. Generating Reports

Four report types available:
- **Product Overview** — Complete product description with component inventory
- **Component Analysis** — Detailed analysis of specific components
- **System Architecture** — Architecture with communication map and security surface
- **Investigation Summary** — Synthesised findings from your research

Export as PDF, Markdown, JSON, or HTML.

## 9. Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend not starting | Check Python is installed and port 8000 is free |
| Ollama disconnected | Run `ollama serve` in a terminal |
| Slow responses | Ensure Ollama model is loaded, consider a GPU |
| OCR quality poor | Use high-resolution images, 300+ DPI |
| Import failures | Check file is not corrupted and format is supported |

## 10. Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Enter | Send message |
| Shift+Enter | New line in message |
