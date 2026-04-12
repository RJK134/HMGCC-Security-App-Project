"""Data export/import and model swap for air-gapped updates."""

import json
import shutil
import sqlite3
import zipfile
from datetime import datetime, timezone
from pathlib import Path

VERSION = "0.1.0"


class SRAUpdater:
    """Manage data portability and model updates."""

    def __init__(self, data_dir: Path) -> None:
        self._data_dir = data_dir

    def export_data(self, output_path: Path) -> Path:
        """Export all user data to a portable .sra-backup archive.

        Args:
            output_path: Where to write the archive.

        Returns:
            Path to the created archive.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        archive = output_path.with_suffix(".sra-backup")

        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
            # Manifest
            manifest = {
                "version": VERSION,
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "files": [],
            }

            # SQLite database
            db_path = self._data_dir / "sqlite" / "sra.db"
            if db_path.exists():
                zf.write(db_path, "sqlite/sra.db")
                manifest["files"].append("sqlite/sra.db")

            # ChromaDB
            chroma_dir = self._data_dir / "vectordb"
            if chroma_dir.exists():
                for f in chroma_dir.rglob("*"):
                    if f.is_file():
                        arcname = f"vectordb/{f.relative_to(chroma_dir)}"
                        zf.write(f, arcname)
                        manifest["files"].append(arcname)

            # Uploads
            uploads_dir = self._data_dir / "uploads"
            if uploads_dir.exists():
                for f in uploads_dir.rglob("*"):
                    if f.is_file():
                        arcname = f"uploads/{f.relative_to(uploads_dir)}"
                        zf.write(f, arcname)
                        manifest["files"].append(arcname)

            zf.writestr("manifest.json", json.dumps(manifest, indent=2))

        return archive

    def import_data(self, archive_path: Path) -> dict:
        """Import data from a .sra-backup archive.

        Args:
            archive_path: Path to the archive file.

        Returns:
            Summary dict with import statistics.
        """
        if not archive_path.exists():
            raise FileNotFoundError(f"Archive not found: {archive_path}")

        stats = {"files_imported": 0, "warnings": []}

        with zipfile.ZipFile(archive_path, "r") as zf:
            # Validate manifest
            try:
                manifest = json.loads(zf.read("manifest.json"))
            except (KeyError, json.JSONDecodeError):
                raise ValueError("Invalid archive: missing or corrupt manifest")

            # Check version
            archive_version = manifest.get("version", "unknown")
            if archive_version != VERSION:
                stats["warnings"].append(
                    f"Version mismatch: archive is v{archive_version}, current is v{VERSION}"
                )

            # Extract all files
            for name in zf.namelist():
                if name == "manifest.json":
                    continue
                target = self._data_dir / name
                target.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(name) as src, open(target, "wb") as dst:
                    dst.write(src.read())
                stats["files_imported"] += 1

        return stats

    def get_data_stats(self) -> dict:
        """Get statistics about current data storage."""
        stats: dict = {"version": VERSION}

        db_path = self._data_dir / "sqlite" / "sra.db"
        if db_path.exists():
            stats["database_size_mb"] = round(db_path.stat().st_size / 1024 / 1024, 2)
            try:
                conn = sqlite3.connect(str(db_path))
                stats["projects"] = conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
                stats["documents"] = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
                stats["conversations"] = conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
                stats["chunks"] = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
                conn.close()
            except Exception:
                pass

        chroma_dir = self._data_dir / "vectordb"
        if chroma_dir.exists():
            total = sum(f.stat().st_size for f in chroma_dir.rglob("*") if f.is_file())
            stats["vectordb_size_mb"] = round(total / 1024 / 1024, 2)

        return stats
