# Requirements

## Essential Requirements (MUST HAVE)

| ID    | Requirement                              | Description |
|-------|------------------------------------------|-------------|
| ER-01 | System Architecture Understanding        | Understand system architecture of a selected machine: physical interfaces, data interfaces, protocols, components (filters, fuses, processors, memory, sensors), software (source/binary) across multiple processors and operating systems. |
| ER-02 | Response Validation & Anti-Hallucination | Check and validate responses before publishing to prevent erroneous information and hallucinations. |
| ER-03 | Multi-Modal Input Characterisation       | Characterise from multimedia inputs: manuals, schematics, datasheets, databases, images, code, handwritten annotations. |
| ER-04 | Source Verification & Cross-Referencing  | Verify information by listing sources and cross-checking against high-confidence data (industry publications, academic research, manufacturer docs). |
| ER-05 | Confidence Scoring                       | Flag a confidence score and indicate if more source data is required. |
| ER-06 | Fully Offline Operation                  | Operate on a laptop without internet. Characterise systems and identify vulnerabilities with no connectivity. |
| ER-07 | Intelligent Search & Chat Interface      | Easy-to-use search and intelligent function to query the dataset in a chat-like manner. |
| ER-08 | Conversational Memory                    | Keep memory of queries so conversations can continue over weeks without prompt repetition. |

## Desirable Requirements (SHOULD HAVE)

| ID    | Requirement                    | Description |
|-------|--------------------------------|-------------|
| DR-01 | User Profiling & Adaptation    | Build user profile, adapt to needs, present preferred formats, proactively provide frequent info. |
| DR-02 | Non-English Data Support       | Translate and index non-English data sources. |
| DR-03 | Cultural Bias Mitigation       | Recognise and mitigate cultural biases for nuanced understanding. |
| DR-04 | Offline Update Mechanism       | Mechanism for periodic updates of core tool and algorithms while offline. |

## Non-Functional Requirements

| ID     | Requirement     | Target |
|--------|-----------------|--------|
| NFR-01 | Performance     | Query response <10s without GPU, <3s with GPU |
| NFR-02 | Scalability     | Handle several thousand documents per investigation |
| NFR-03 | Security        | All data local. No telemetry, no network calls. OFFICIAL classification suitable. |
| NFR-04 | Portability     | Run on standard Windows or Linux laptop. No specialised hardware. |
| NFR-05 | Usability       | Chat-like interface, intuitive without training, drag-and-drop ingestion. |
| NFR-06 | Extensibility   | Support future addition of new parsers, LLM models, and indexing algorithms. |
| NFR-07 | Data Integrity  | No data corruption/loss. Maintain provenance metadata for all sources. |

## Constraints
- C-01: Must work without an internet connection.

## Out of Scope
- Autonomous discovery/search for source data. Test data provided by HMGCC.
