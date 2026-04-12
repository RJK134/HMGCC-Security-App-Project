# Known Limitations — Honest Assessment

## LLM Quality
- Quantised 7B models may miss nuance in complex technical questions
- Response quality varies by model — larger models (13B+) are better but slower on CPU
- The LLM may occasionally generate plausible-sounding but incorrect technical details,
  which is why every response passes through the validation pipeline

## OCR Accuracy
- Printed text: 85-95% accuracy (good)
- Handwritten annotations: 60-80% accuracy (requires human review)
- Complex schematics: OCR extracts text labels but cannot interpret circuit topology
- Very low resolution or blurry images will produce poor results

## Architecture Extraction
- Depends entirely on LLM interpretation of document text
- Components not explicitly named in documents will be missed
- Interface mappings are inferred from text, not from actual schematic analysis
- Best results come from well-structured datasheets and manuals

## Confidence Scoring
- Heuristic-based: correlates with source quality and coverage but is not statistically calibrated
- A score of 80 does not mean "80% probability of being correct"
- Best used as a relative indicator (higher is better) rather than an absolute measure

## Scale Limitations
- Recommended maximum: ~5,000 documents per project
- ChromaDB performance may degrade with very large collections (>100,000 chunks)
- BM25 index is rebuilt from scratch on changes — slow for very large datasets

## Single User
- Current version is a single-user tool
- No authentication, authorisation, or access control
- Not suitable for shared server deployment without additional security layers

## Translation
- Non-English translation uses the general-purpose LLM
- Technical terms may be mistranslated or lost
- Manual review of translated content is recommended

## The Tool Does Not Replace Expert Analysis
This tool accelerates the research phase by organising and querying source material.
It does not perform vulnerability analysis, threat modelling, or risk assessment
autonomously. A qualified security researcher must interpret the findings and
apply domain expertise.
