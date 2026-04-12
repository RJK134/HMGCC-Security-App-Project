"""Component and interface extraction from ingested documents using LLM."""

from uuid import UUID

from pydantic import BaseModel, Field

from core.database.connection import DatabaseManager
from core.logging import get_logger
from core.rag.llm_client import OllamaClient

log = get_logger(__name__)

_EXTRACT_PROMPT = """Analyse the following technical document excerpts about an industrial product.
Extract ALL components, interfaces, protocols, and software mentioned.

Return your answer in EXACTLY this format (one item per line):
COMPONENT: name | type | description
INTERFACE: name | connects_from | connects_to
PROTOCOL: name | layer | description
SOFTWARE: name | type | version_if_known

Types for COMPONENT: processor, memory, sensor, actuator, filter, fuse, regulator, transceiver, connector, other
Types for SOFTWARE: os, firmware, library, driver, application

Document excerpts:
{text}

Extract every component, interface, protocol, and software item you can find. Be thorough."""


class ExtractedComponent(BaseModel):
    """A hardware or software component identified in the documents."""
    name: str
    component_type: str
    description: str = ""
    source_document: str = ""
    source_page: int | None = None


class ExtractedInterface(BaseModel):
    """An interface or connection between components."""
    name: str
    connects_from: str = ""
    connects_to: str = ""
    source_document: str = ""


class ExtractedProtocol(BaseModel):
    """A communication protocol identified in the documents."""
    name: str
    layer: str = ""
    description: str = ""
    source_document: str = ""


class ExtractedSoftware(BaseModel):
    """A software component (OS, firmware, library)."""
    name: str
    software_type: str = ""
    version: str = ""
    source_document: str = ""


class ExtractionResult(BaseModel):
    """Complete extraction result from document analysis."""
    components: list[ExtractedComponent] = Field(default_factory=list)
    interfaces: list[ExtractedInterface] = Field(default_factory=list)
    protocols: list[ExtractedProtocol] = Field(default_factory=list)
    software: list[ExtractedSoftware] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ArchitectureExtractor:
    """Extract system components and interfaces from indexed documents.

    Args:
        db: Database manager for reading chunks.
        ollama_client: LLM for extraction.
    """

    def __init__(self, db: DatabaseManager, ollama_client: OllamaClient) -> None:
        self._db = db
        self._llm = ollama_client

    def extract(self, project_id: UUID) -> ExtractionResult:
        """Extract all components, interfaces, protocols, and software for a project.

        Reads chunks from the database, batches them, and sends to the LLM
        for structured extraction.

        Args:
            project_id: Project UUID.

        Returns:
            ExtractionResult with all extracted entities.
        """
        conn = self._db.get_connection()

        # Load representative chunks (first chunk from each document + headings)
        rows = conn.execute(
            """SELECT c.content, c.section_heading, d.filename, c.page_number
               FROM chunks c JOIN documents d ON c.document_id = d.id
               WHERE d.project_id = ? AND c.chunk_index < 5
               ORDER BY d.filename, c.chunk_index
               LIMIT 50""",
            (str(project_id),),
        ).fetchall()

        if not rows:
            return ExtractionResult(warnings=["No documents found in this project."])

        # Build text for LLM
        text_parts = []
        for row in rows:
            header = f"[{row['filename']}"
            if row["page_number"]:
                header += f", Page {row['page_number']}"
            if row["section_heading"]:
                header += f", Section: {row['section_heading']}"
            header += "]"
            text_parts.append(f"{header}\n{row['content'][:500]}")

        combined = "\n\n---\n\n".join(text_parts)
        prompt = _EXTRACT_PROMPT.format(text=combined[:4000])

        try:
            response = self._llm.generate(prompt, system_prompt="")
            if not isinstance(response, str):
                response = "".join(response)
            result = self._parse_extraction(response, rows)
            log.info(
                "architecture_extracted",
                project_id=str(project_id),
                components=len(result.components),
                interfaces=len(result.interfaces),
                protocols=len(result.protocols),
            )
            return result
        except Exception as e:
            log.error("architecture_extraction_failed", error=str(e))
            return ExtractionResult(warnings=[f"Extraction failed: {e}"])

    def _parse_extraction(self, response: str, rows: list) -> ExtractionResult:
        """Parse the LLM extraction response into structured entities."""
        result = ExtractionResult()

        for line in response.strip().split("\n"):
            line = line.strip()
            if not line:
                continue

            try:
                if line.startswith("COMPONENT:"):
                    parts = [p.strip() for p in line[10:].split("|")]
                    if len(parts) >= 2:
                        result.components.append(ExtractedComponent(
                            name=parts[0], component_type=parts[1],
                            description=parts[2] if len(parts) > 2 else "",
                        ))
                elif line.startswith("INTERFACE:"):
                    parts = [p.strip() for p in line[10:].split("|")]
                    if len(parts) >= 2:
                        result.interfaces.append(ExtractedInterface(
                            name=parts[0],
                            connects_from=parts[1] if len(parts) > 1 else "",
                            connects_to=parts[2] if len(parts) > 2 else "",
                        ))
                elif line.startswith("PROTOCOL:"):
                    parts = [p.strip() for p in line[9:].split("|")]
                    if len(parts) >= 1:
                        result.protocols.append(ExtractedProtocol(
                            name=parts[0],
                            layer=parts[1] if len(parts) > 1 else "",
                            description=parts[2] if len(parts) > 2 else "",
                        ))
                elif line.startswith("SOFTWARE:"):
                    parts = [p.strip() for p in line[9:].split("|")]
                    if len(parts) >= 1:
                        result.software.append(ExtractedSoftware(
                            name=parts[0],
                            software_type=parts[1] if len(parts) > 1 else "",
                            version=parts[2] if len(parts) > 2 else "",
                        ))
            except Exception:
                continue  # Skip unparseable lines

        # Deduplicate by name
        result.components = list({c.name: c for c in result.components}.values())
        result.interfaces = list({i.name: i for i in result.interfaces}.values())
        result.protocols = list({p.name: p for p in result.protocols}.values())
        result.software = list({s.name: s for s in result.software}.values())

        return result
