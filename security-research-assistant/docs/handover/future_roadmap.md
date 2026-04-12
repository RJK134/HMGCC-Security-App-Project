# Future Roadmap — Phase 2 Proposals

## If Funded: Proposed Enhancements

### 1. Autonomous Data Collection
Web scraping pipeline for datasheets, technical forums, and component databases.
Used during the online preparation phase; data transferred to air-gapped tool via USB.

### 2. ML-Based Schematic Analysis
Computer vision model trained to identify components and connections in circuit
diagram images — beyond OCR text extraction to actual component recognition.

### 3. Multi-User Collaboration
Shared projects with role-based access control. Multiple investigators working
on the same product simultaneously with conflict resolution.

### 4. Advanced Threat Modelling
Integration with MITRE ATT&CK for ICS framework. Automated mapping of discovered
components and interfaces to known attack vectors and vulnerabilities.

### 5. Plugin Architecture
Allow HMGCC to develop custom parsers, analysis modules, and report templates
without modifying the core application.

### 6. Improved Non-English Support
Dedicated translation models for Chinese, Japanese, Korean, and Russian —
common in ICS component documentation from international manufacturers.

### 7. Hardware Acceleration
CUDA/ROCm optimisation for GPU inference. Benchmarking and profiling for
optimal performance on HMGCC target hardware.

### 8. Model Fine-Tuning
Fine-tune the LLM on ICS-specific vocabulary, component databases, and
security assessment patterns for improved answer quality.

## Estimated Phase 2 Costs
- Development: £80,000-120,000 (16-24 weeks, 2 FTE)
- ML model training infrastructure: £5,000
- Testing and validation: £10,000
- Total: £95,000-135,000
