"""System architecture extraction and visualisation endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends

from backend.dependencies import get_db, get_ollama_client
from core.architecture.extractor import ArchitectureExtractor
from core.architecture.mapper import ArchitectureMapper
from core.architecture.visualiser import ArchitectureVisualiser
from core.database.connection import DatabaseManager
from core.logging import get_logger
from core.rag.llm_client import OllamaClient

log = get_logger(__name__)
router = APIRouter(prefix="/architecture", tags=["architecture"])


@router.get("/{project_id}")
def get_architecture(
    project_id: UUID,
    db: DatabaseManager = Depends(get_db),
    ollama: OllamaClient = Depends(get_ollama_client),
) -> dict:
    """Get the system architecture for a project.

    Extracts components from documents, builds a graph, generates a summary.
    """
    extractor = ArchitectureExtractor(db, ollama)
    mapper = ArchitectureMapper()
    visualiser = ArchitectureVisualiser(ollama)

    extraction = extractor.extract(project_id)
    graph = mapper.build_graph(extraction)
    summary = visualiser.generate_summary(extraction, graph)
    graph.summary = summary

    return {
        "graph": visualiser.export_dict(graph),
        "extraction": {
            "components": [c.model_dump() for c in extraction.components],
            "interfaces": [i.model_dump() for i in extraction.interfaces],
            "protocols": [p.model_dump() for p in extraction.protocols],
            "software": [s.model_dump() for s in extraction.software],
        },
        "summary": summary,
        "warnings": extraction.warnings + graph.incomplete_areas,
    }


@router.post("/{project_id}/extract")
def trigger_extraction(
    project_id: UUID,
    db: DatabaseManager = Depends(get_db),
    ollama: OllamaClient = Depends(get_ollama_client),
) -> dict:
    """Trigger a fresh architecture extraction for a project."""
    extractor = ArchitectureExtractor(db, ollama)
    extraction = extractor.extract(project_id)

    return {
        "status": "ok",
        "components": len(extraction.components),
        "interfaces": len(extraction.interfaces),
        "protocols": len(extraction.protocols),
        "software": len(extraction.software),
        "warnings": extraction.warnings,
    }
