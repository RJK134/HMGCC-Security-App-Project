"""Data maintenance API — export, import, version, and stats."""

import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import FileResponse

from backend.config import Settings
from backend.dependencies import get_app_settings, get_db
from core.database.connection import DatabaseManager
from core.logging import get_logger

log = get_logger(__name__)
router = APIRouter(prefix="/maintenance", tags=["maintenance"])

VERSION = "0.1.0"


def _get_updater(settings: Settings):
    from scripts.update import SRAUpdater
    return SRAUpdater(Path(settings.chroma_path).parent)


@router.get("/version")
def get_version(settings: Settings = Depends(get_app_settings)) -> dict:
    """Return current version and data statistics."""
    updater = _get_updater(settings)
    stats = updater.get_data_stats()
    return {"version": VERSION, "stats": stats}


@router.post("/export")
def export_data(settings: Settings = Depends(get_app_settings)):
    """Export all user data as a downloadable .sra-backup file."""
    updater = _get_updater(settings)
    tmp = Path(tempfile.mkdtemp()) / "sra-export"
    archive = updater.export_data(tmp)
    return FileResponse(
        str(archive),
        media_type="application/zip",
        filename="sra-data-export.sra-backup",
    )


@router.post("/import")
async def import_data(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_app_settings),
) -> dict:
    """Import data from a .sra-backup file."""
    tmp = Path(tempfile.mkdtemp()) / (file.filename or "import.sra-backup")
    with open(tmp, "wb") as f:
        content = await file.read()
        f.write(content)

    updater = _get_updater(settings)
    stats = updater.import_data(tmp)
    return {"status": "ok", "stats": stats}
