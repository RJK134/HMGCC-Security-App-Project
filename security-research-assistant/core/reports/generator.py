"""Report generation — compile research findings into structured reports."""

import time
from uuid import UUID

from core.database.connection import DatabaseManager
from core.logging import get_logger
from core.rag.llm_client import OllamaClient
from core.reports.templates import (
    TEMPLATE_SECTIONS,
    TEMPLATE_TITLES,
    Report,
    ReportOptions,
    ReportSection,
    ReportType,
)

log = get_logger(__name__)

_SECTION_PROMPT = """You are writing a section of a technical security research report.
Project: {project_name}
Section: {heading}
Purpose: {purpose}

Available data from the project's document library:
{data}

IMPORTANT RULES:
1. ONLY cite documents that appear in the data above. Do NOT invent document names.
2. Use the exact filenames shown in square brackets (e.g., [Source: actual_filename.pdf]).
3. If data is insufficient for this section, say "Data not available" — do NOT fabricate.
4. Use the actual project name "{project_name}" — do NOT invent project names.
5. Write in clear, professional technical prose.
Keep to approximately {target_words} words."""


class ReportGenerator:
    """Generate structured reports from project data using LLM assistance.

    Args:
        db: Database manager for reading project data.
        ollama_client: LLM for narrative generation.
    """

    def __init__(self, db: DatabaseManager, ollama_client: OllamaClient) -> None:
        self._db = db
        self._llm = ollama_client

    def generate_report(
        self,
        project_id: UUID,
        report_type: ReportType,
        options: ReportOptions | None = None,
    ) -> Report:
        """Generate a report of the specified type for a project.

        Args:
            project_id: Project UUID.
            report_type: Which report template to use.
            options: Generation options.

        Returns:
            Complete Report with all sections.
        """
        opts = options or ReportOptions()
        start = time.time()

        # Gather project data
        data = self._gather_data(project_id, report_type, opts)
        project_name = data.get("_project_name", "Unknown Project")

        # Generate sections
        template = TEMPLATE_SECTIONS[report_type]
        sections: list[ReportSection] = []
        llm_calls = 0

        for heading, purpose in template:
            section_data = data.get(heading, data.get("_default", "No data available."))
            content = self._generate_section(heading, purpose, section_data, project_name)
            llm_calls += 1
            sections.append(ReportSection(
                heading=heading,
                content=content,
                confidence_note=self._confidence_note(heading, section_data),
            ))

        # Add custom sections
        if opts.custom_sections:
            for custom in opts.custom_sections:
                content = self._generate_section(custom, "Additional analysis", data.get("_default", ""))
                llm_calls += 1
                sections.append(ReportSection(heading=custom, content=content))

        elapsed = time.time() - start
        report = Report(
            project_id=project_id,
            report_type=report_type,
            title=TEMPLATE_TITLES[report_type],
            sections=sections,
            metadata={
                "generation_time_seconds": round(elapsed, 1),
                "llm_calls": llm_calls,
                "sources_used": data.get("_doc_count", 0),
            },
        )

        # Store in DB
        self._store_report(report)

        log.info(
            "report_generated",
            report_id=str(report.id),
            type=report_type.value,
            sections=len(sections),
            time=round(elapsed, 1),
        )
        return report

    def _gather_data(self, project_id: UUID, report_type: ReportType, opts: ReportOptions) -> dict:
        """Gather all relevant data for report generation."""
        conn = self._db.get_connection()
        data: dict = {}

        # Get project name
        project_row = conn.execute(
            "SELECT name FROM projects WHERE id = ?", (str(project_id),)
        ).fetchone()
        data["_project_name"] = project_row["name"] if project_row else "Unknown Project"

        # Documents
        docs = conn.execute(
            "SELECT filename, filetype, source_tier, size_bytes, page_count FROM documents WHERE project_id = ?",
            (str(project_id),),
        ).fetchall()

        doc_summary = "\n".join(
            f"- {d['filename']} ({d['filetype']}, {d['source_tier']})"
            for d in docs
        )
        data["Appendix: Source Documents"] = doc_summary or "No documents imported."
        data["Source Bibliography"] = doc_summary or "No documents imported."
        data["Source Library Summary"] = f"{len(docs)} documents imported.\n{doc_summary}"
        data["_doc_count"] = len(docs)

        # Architecture data
        chunks = conn.execute(
            """SELECT c.content, c.section_heading, d.filename
               FROM chunks c JOIN documents d ON c.document_id = d.id
               WHERE d.project_id = ? AND c.chunk_index < 3
               ORDER BY d.filename LIMIT 30""",
            (str(project_id),),
        ).fetchall()

        tech_text = "\n".join(
            f"[{r['filename']}, {r['section_heading'] or 'General'}]: {r['content'][:300]}"
            for r in chunks
        )
        data["_default"] = tech_text or "No indexed content available."

        # Architecture sections use the same data
        for key in ("System Architecture Overview", "Architecture Overview",
                     "Component Hierarchy", "Communication Map", "External Interfaces",
                     "Security Surface", "Component Inventory", "Interface Map",
                     "Component Identification", "Technical Specifications",
                     "Interfaces and Connections", "Software/Firmware",
                     "Known Vulnerabilities"):
            data[key] = tech_text

        # Conversations (for investigation summary)
        convs = conn.execute(
            "SELECT title, summary FROM conversations WHERE project_id = ? ORDER BY updated_at DESC LIMIT 10",
            (str(project_id),),
        ).fetchall()

        conv_text = "\n".join(
            f"- {c['title']}: {c['summary'] or '(no summary)'}"
            for c in convs
        )

        # Pinned facts
        facts = conn.execute(
            """SELECT pf.content FROM pinned_facts pf
               JOIN conversations cv ON pf.conversation_id = cv.id
               WHERE cv.project_id = ?""",
            (str(project_id),),
        ).fetchall()
        facts_text = "\n".join(f"- {f['content']}" for f in facts)

        data["Key Findings"] = f"Pinned facts:\n{facts_text}\n\nConversation summaries:\n{conv_text}" if facts_text else conv_text or "No conversations recorded."
        data["Questions Explored"] = conv_text or "No conversations recorded."
        data["Technical Discoveries"] = facts_text or "No pinned facts."
        data["Open Questions"] = "Based on conversations: " + conv_text if conv_text else "No data."
        data["Investigation Overview"] = f"Project with {len(docs)} documents and {len(convs)} conversations."

        # Confidence / gaps
        tier_counts: dict[str, int] = {}
        for d in docs:
            tier_counts[d["source_tier"]] = tier_counts.get(d["source_tier"], 0) + 1
        tier_str = ", ".join(f"{k}: {v}" for k, v in tier_counts.items())
        data["Confidence Assessment"] = f"Source tier breakdown: {tier_str}. {len(facts)} pinned facts."
        data["Source Confidence"] = f"Source tiers: {tier_str}."
        data["Information Gaps"] = tech_text  # LLM will identify gaps
        data["Gaps and Recommendations"] = tech_text
        data["Recommendations"] = tech_text

        # Executive / overview
        data["Executive Summary"] = tech_text
        data["Product Identification"] = tech_text
        data["References"] = doc_summary

        return data

    def _generate_section(self, heading: str, purpose: str, data: str, project_name: str = "Unknown") -> str:
        """Generate content for a single report section using the LLM."""
        prompt = _SECTION_PROMPT.format(
            heading=heading, purpose=purpose,
            data=data[:3000], target_words=200,
            project_name=project_name,
        )
        try:
            response = self._llm.generate(prompt, system_prompt="")
            if not isinstance(response, str):
                response = "".join(response)
            return response.strip()
        except Exception as e:
            log.warning("section_generation_failed", heading=heading, error=str(e))
            return f"[Section generation failed: {e}. Data available: {data[:200]}...]"

    def _confidence_note(self, heading: str, data: str) -> str | None:
        """Generate a confidence note for a section based on data availability."""
        if not data or data == "No data available." or len(data) < 50:
            return "Low confidence: insufficient source data for this section."
        return None

    def _store_report(self, report: Report) -> None:
        """Store a generated report in SQLite."""
        import json
        conn = self._db.get_connection()

        # Ensure reports table exists
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                report_type TEXT NOT NULL,
                title TEXT NOT NULL,
                sections_json TEXT NOT NULL,
                metadata_json TEXT DEFAULT '{}',
                generated_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

        sections_json = json.dumps([s.model_dump(mode="json") for s in report.sections])
        conn.execute(
            "INSERT OR REPLACE INTO reports (id, project_id, report_type, title, sections_json, metadata_json, generated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (str(report.id), str(report.project_id), report.report_type.value,
             report.title, sections_json, json.dumps(report.metadata),
             report.generated_at.isoformat()),
        )
        conn.commit()
