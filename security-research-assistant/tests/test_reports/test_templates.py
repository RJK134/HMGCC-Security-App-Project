"""Tests for report templates."""

from core.reports.templates import (
    TEMPLATE_SECTIONS,
    TEMPLATE_TITLES,
    ReportType,
)


class TestReportTemplates:
    def test_all_types_have_sections(self) -> None:
        for rt in ReportType:
            assert rt in TEMPLATE_SECTIONS
            assert len(TEMPLATE_SECTIONS[rt]) >= 3

    def test_all_types_have_titles(self) -> None:
        for rt in ReportType:
            assert rt in TEMPLATE_TITLES
            assert len(TEMPLATE_TITLES[rt]) > 5

    def test_sections_are_tuples(self) -> None:
        for rt, sections in TEMPLATE_SECTIONS.items():
            for heading, purpose in sections:
                assert isinstance(heading, str)
                assert isinstance(purpose, str)

    def test_report_type_values(self) -> None:
        assert ReportType.PRODUCT_OVERVIEW.value == "product_overview"
        assert ReportType.INVESTIGATION_SUMMARY.value == "investigation_summary"
