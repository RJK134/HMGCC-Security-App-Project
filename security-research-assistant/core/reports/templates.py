"""Report structure templates defining section layouts for each report type."""

from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ReportType(str, Enum):
    """Available report types."""
    PRODUCT_OVERVIEW = "product_overview"
    COMPONENT_ANALYSIS = "component_analysis"
    SYSTEM_ARCHITECTURE = "system_architecture"
    INVESTIGATION_SUMMARY = "investigation_summary"


class ReportSection(BaseModel):
    """A section (or subsection) of a report."""
    heading: str
    content: str = ""
    subsections: list["ReportSection"] = Field(default_factory=list)
    citations: list[dict] = Field(default_factory=list)
    confidence_note: str | None = None


class Report(BaseModel):
    """A generated report with all sections."""
    id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    report_type: ReportType
    title: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sections: list[ReportSection] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class ReportOptions(BaseModel):
    """Options controlling report generation."""
    include_raw_sources: bool = False
    include_conversation_history: bool = False
    component_filter: list[UUID] | None = None
    max_length: int | None = None
    custom_sections: list[str] | None = None


# Section definitions per template
_PRODUCT_OVERVIEW_SECTIONS = [
    ("Executive Summary", "High-level product description and purpose"),
    ("Product Identification", "Manufacturer, model, version, serial info"),
    ("System Architecture Overview", "Architecture from extracted components and interfaces"),
    ("Component Inventory", "Table of all identified components with types and specs"),
    ("Interface Map", "Table of all interfaces and protocols"),
    ("Source Library Summary", "Count and types of documents, tier breakdown"),
    ("Information Gaps", "Known unknowns, missing data, low-confidence areas"),
    ("Appendix: Source Documents", "Full list of imported documents with tiers"),
]

_COMPONENT_ANALYSIS_SECTIONS = [
    ("Component Identification", "Name, part number, manufacturer, type"),
    ("Technical Specifications", "All known specs from source documents"),
    ("Interfaces and Connections", "How this component connects to the system"),
    ("Software/Firmware", "Any software associated with this component"),
    ("Known Vulnerabilities", "Vulnerability information found in sources"),
    ("Source Confidence", "Confidence score and source breakdown"),
    ("References", "List of source documents for this component"),
]

_ARCHITECTURE_SECTIONS = [
    ("Architecture Overview", "Natural language system architecture description"),
    ("Component Hierarchy", "Layered view from system to sub-components"),
    ("Communication Map", "All data paths and protocols"),
    ("External Interfaces", "Ports, connections, and interfaces exposed externally"),
    ("Security Surface", "Debug ports, network connections, update mechanisms"),
    ("Gaps and Recommendations", "Missing information and next investigation steps"),
]

_INVESTIGATION_SECTIONS = [
    ("Investigation Overview", "Project name, dates, scope"),
    ("Key Findings", "Major discoveries from conversations and pinned facts"),
    ("Questions Explored", "Summary of questions asked and key answers"),
    ("Technical Discoveries", "Specific technical details uncovered"),
    ("Open Questions", "Unanswered questions and further investigation areas"),
    ("Confidence Assessment", "Overall confidence in findings, weakest areas"),
    ("Recommendations", "Suggested next steps for the investigation"),
    ("Source Bibliography", "All documents with tier classification"),
]

TEMPLATE_SECTIONS: dict[ReportType, list[tuple[str, str]]] = {
    ReportType.PRODUCT_OVERVIEW: _PRODUCT_OVERVIEW_SECTIONS,
    ReportType.COMPONENT_ANALYSIS: _COMPONENT_ANALYSIS_SECTIONS,
    ReportType.SYSTEM_ARCHITECTURE: _ARCHITECTURE_SECTIONS,
    ReportType.INVESTIGATION_SUMMARY: _INVESTIGATION_SECTIONS,
}

TEMPLATE_TITLES: dict[ReportType, str] = {
    ReportType.PRODUCT_OVERVIEW: "Product Overview Report",
    ReportType.COMPONENT_ANALYSIS: "Component Analysis Report",
    ReportType.SYSTEM_ARCHITECTURE: "System Architecture Report",
    ReportType.INVESTIGATION_SUMMARY: "Investigation Summary Report",
}
