"""Report generation and export API endpoints."""

import json
import tempfile
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from pydantic import BaseModel

from backend.dependencies import get_db, get_ollama_client
from core.database.connection import DatabaseManager
from core.logging import get_logger
from core.rag.llm_client import OllamaClient
from core.reports.exporter import ReportExporter
from core.reports.generator import ReportGenerator
from core.reports.templates import Report, ReportOptions, ReportSection, ReportType

log = get_logger(__name__)
router = APIRouter(prefix="/reports", tags=["reports"])


class GenerateRequest(BaseModel):
    project_id: UUID
    report_type: ReportType
    options: ReportOptions | None = None


@router.post("/generate")
def generate_report(
    request: GenerateRequest,
    db: DatabaseManager = Depends(get_db),
    ollama: OllamaClient = Depends(get_ollama_client),
) -> dict:
    """Generate a new report for a project. May take 30-60 seconds."""
    generator = ReportGenerator(db, ollama)
    report = generator.generate_report(
        request.project_id, request.report_type, request.options,
    )
    return {"report": report.model_dump(mode="json")}


@router.get("")
def list_reports(
    project_id: UUID,
    db: DatabaseManager = Depends(get_db),
) -> dict:
    """List previously generated reports for a project."""
    conn = db.get_connection()
    # Ensure table exists
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id TEXT PRIMARY KEY, project_id TEXT NOT NULL,
            report_type TEXT NOT NULL, title TEXT NOT NULL,
            sections_json TEXT NOT NULL, metadata_json TEXT DEFAULT '{}',
            generated_at TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    """)
    rows = conn.execute(
        "SELECT id, report_type, title, generated_at, metadata_json FROM reports WHERE project_id = ? ORDER BY generated_at DESC",
        (str(project_id),),
    ).fetchall()

    reports = []
    for r in rows:
        meta = json.loads(r["metadata_json"] or "{}")
        reports.append({
            "id": r["id"], "report_type": r["report_type"],
            "title": r["title"], "generated_at": r["generated_at"],
            "metadata": meta,
        })
    return {"reports": reports}


@router.get("/{report_id}")
def get_report(
    report_id: UUID,
    db: DatabaseManager = Depends(get_db),
) -> dict:
    """Get a full report with all sections."""
    conn = db.get_connection()
    row = conn.execute("SELECT * FROM reports WHERE id = ?", (str(report_id),)).fetchone()
    if not row:
        return {"error": "Report not found"}

    sections = json.loads(row["sections_json"] or "[]")
    return {
        "report": {
            "id": row["id"], "project_id": row["project_id"],
            "report_type": row["report_type"], "title": row["title"],
            "generated_at": row["generated_at"],
            "sections": sections,
            "metadata": json.loads(row["metadata_json"] or "{}"),
        },
    }


@router.get("/{report_id}/export")
def export_report(
    report_id: UUID,
    format: str = Query(default="markdown"),
    db: DatabaseManager = Depends(get_db),
):
    """Export a report in the requested format (markdown, pdf, json, html)."""
    conn = db.get_connection()
    row = conn.execute("SELECT * FROM reports WHERE id = ?", (str(report_id),)).fetchone()
    if not row:
        return {"error": "Report not found"}

    # Reconstruct Report model
    sections = [ReportSection(**s) for s in json.loads(row["sections_json"] or "[]")]
    report = Report(
        id=UUID(row["id"]), project_id=UUID(row["project_id"]),
        report_type=ReportType(row["report_type"]), title=row["title"],
        sections=sections, metadata=json.loads(row["metadata_json"] or "{}"),
    )

    exporter = ReportExporter()

    if format == "markdown":
        return PlainTextResponse(exporter.export_markdown(report), media_type="text/markdown")
    elif format == "pdf":
        tmp = Path(tempfile.mkdtemp()) / f"{report_id}.pdf"
        exporter.export_pdf(report, tmp)
        return FileResponse(str(tmp), media_type="application/pdf", filename=f"{report.title}.pdf")
    elif format == "json":
        return PlainTextResponse(exporter.export_json(report), media_type="application/json")
    elif format == "html":
        return HTMLResponse(exporter.export_html(report))
    else:
        return {"error": f"Unsupported format: {format}"}


@router.delete("/{report_id}")
def delete_report(
    report_id: UUID,
    db: DatabaseManager = Depends(get_db),
) -> dict:
    """Delete a generated report."""
    conn = db.get_connection()
    conn.execute("DELETE FROM reports WHERE id = ?", (str(report_id),))
    conn.commit()
    return {"status": "ok", "report_id": str(report_id)}
