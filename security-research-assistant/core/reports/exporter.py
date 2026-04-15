"""Report export — Markdown, PDF, JSON, and HTML formats."""

import json
from pathlib import Path

from core.logging import get_logger
from core.reports.templates import Report

log = get_logger(__name__)


class ReportExporter:
    """Export reports in multiple formats."""

    def export_markdown(self, report: Report) -> str:
        """Export a report as well-formatted Markdown.

        Args:
            report: The report to export.

        Returns:
            Markdown string.
        """
        lines: list[str] = []
        lines.append("**OFFICIAL**")
        lines.append("")
        lines.append(f"# {report.title}")
        lines.append("")
        lines.append(f"**Generated:** {report.generated_at.strftime('%Y-%m-%d %H:%M UTC')}")
        lines.append(f"**Report Type:** {report.report_type.value.replace('_', ' ').title()}")
        lines.append("")
        lines.append("---")
        lines.append("")

        for section in report.sections:
            lines.append(f"## {section.heading}")
            lines.append("")
            lines.append(section.content)
            lines.append("")

            if section.confidence_note:
                lines.append(f"> **Note:** {section.confidence_note}")
                lines.append("")

            for sub in section.subsections:
                lines.append(f"### {sub.heading}")
                lines.append("")
                lines.append(sub.content)
                lines.append("")

            lines.append("---")
            lines.append("")

        # Metadata footer
        lines.append("## Report Metadata")
        lines.append("")
        for k, v in report.metadata.items():
            lines.append(f"- **{k.replace('_', ' ').title()}:** {v}")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("**OFFICIAL**")
        lines.append("")

        return "\n".join(lines)

    def export_pdf(self, report: Report, output_path: Path) -> Path:
        """Export a report as a PDF document using reportlab.

        Args:
            report: The report to export.
            output_path: File path for the output PDF.

        Returns:
            Path to the generated PDF file.
        """
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            PageBreak,
            Paragraph,
            SimpleDocTemplate,
            Spacer,
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        doc = SimpleDocTemplate(
            str(output_path), pagesize=A4,
            leftMargin=25 * mm, rightMargin=25 * mm,
            topMargin=25 * mm, bottomMargin=20 * mm,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "ReportTitle", parent=styles["Title"], fontSize=20, spaceAfter=12,
        )
        heading_style = ParagraphStyle(
            "SectionHeading", parent=styles["Heading2"], fontSize=14,
            spaceBefore=16, spaceAfter=8,
        )
        body_style = ParagraphStyle(
            "ReportBody", parent=styles["Normal"], fontSize=10,
            leading=14, spaceAfter=8,
        )
        note_style = ParagraphStyle(
            "ConfidenceNote", parent=styles["Normal"], fontSize=9,
            textColor="gray", leftIndent=10, spaceAfter=8,
        )
        meta_style = ParagraphStyle(
            "MetaInfo", parent=styles["Normal"], fontSize=9,
            textColor="gray", spaceAfter=4,
        )

        story: list = []

        # Cover page
        story.append(Spacer(1, 60 * mm))
        story.append(Paragraph(report.title, title_style))
        story.append(Spacer(1, 10 * mm))
        story.append(Paragraph(
            f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M UTC')}",
            meta_style,
        ))
        story.append(Paragraph(
            f"Report Type: {report.report_type.value.replace('_', ' ').title()}",
            meta_style,
        ))
        story.append(Paragraph("OFFICIAL", meta_style))
        story.append(PageBreak())

        # Table of contents
        story.append(Paragraph("Table of Contents", heading_style))
        for i, section in enumerate(report.sections, 1):
            story.append(Paragraph(f"{i}. {section.heading}", body_style))
        story.append(PageBreak())

        # Sections
        for section in report.sections:
            story.append(Paragraph(section.heading, heading_style))

            # Split content into paragraphs for proper PDF rendering
            for para in section.content.split("\n\n"):
                para = para.strip()
                if para:
                    # Escape XML characters for reportlab
                    safe = para.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    story.append(Paragraph(safe, body_style))

            if section.confidence_note:
                safe_note = section.confidence_note.replace("&", "&amp;").replace("<", "&lt;")
                story.append(Paragraph(f"Note: {safe_note}", note_style))

            story.append(Spacer(1, 5 * mm))

        doc.build(story)
        log.info("pdf_exported", path=str(output_path))
        return output_path

    def export_json(self, report: Report) -> str:
        """Export a report as structured JSON.

        Args:
            report: The report to export.

        Returns:
            JSON string.
        """
        return report.model_dump_json(indent=2)

    def export_html(self, report: Report) -> str:
        """Export a report as self-contained HTML with embedded CSS.

        Args:
            report: The report to export.

        Returns:
            HTML string.
        """
        sections_html: list[str] = []
        for section in report.sections:
            content = section.content.replace("\n\n", "</p><p>").replace("\n", "<br>")
            note = ""
            if section.confidence_note:
                note = f'<div class="note">{section.confidence_note}</div>'
            sections_html.append(
                f'<section><h2>{section.heading}</h2><p>{content}</p>{note}</section>'
            )

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{report.title}</title>
<style>
  body {{ font-family: -apple-system, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; color: #1a1a1a; line-height: 1.6; }}
  h1 {{ border-bottom: 2px solid #3b82f6; padding-bottom: 8px; }}
  h2 {{ color: #1e40af; margin-top: 2em; }}
  .meta {{ color: #64748b; font-size: 0.9em; }}
  .note {{ background: #fef3c7; border-left: 3px solid #f59e0b; padding: 8px 12px; margin: 8px 0; font-size: 0.9em; }}
  section {{ margin-bottom: 1.5em; }}
  .classification {{ text-align: center; font-weight: bold; font-size: 0.9em; border: 1px solid #000; padding: 4px; margin-bottom: 16px; letter-spacing: 0.2em; }}
  @media print {{ body {{ max-width: 100%; margin: 0; }} .classification {{ page-break-after: avoid; }} }}
</style>
</head>
<body>
<div class="classification">OFFICIAL</div>
<h1>{report.title}</h1>
<p class="meta">Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M UTC')} |
Type: {report.report_type.value.replace('_', ' ').title()}</p>
<hr>
{"".join(sections_html)}
<div class="classification">OFFICIAL</div>
</body>
</html>"""
