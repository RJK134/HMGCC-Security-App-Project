"""Package the Python backend into a self-contained distribution.

Creates a portable directory with embedded Python, all dependencies,
and a launcher script. No pip or Python installation required on target.
"""

import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = PROJECT_ROOT / "dist" / "backend"


def build() -> Path:
    """Build the backend distribution.

    Returns:
        Path to the distribution directory.
    """
    print("=== Building SRA Backend Package ===")

    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True)

    # Copy source
    for pkg in ("backend", "core"):
        src = PROJECT_ROOT / pkg
        dst = DIST_DIR / pkg
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

    # Copy config
    for f in ("config.yaml", "pyproject.toml"):
        src = PROJECT_ROOT / f
        if src.exists():
            shutil.copy2(src, DIST_DIR / f)

    # Create data directories
    for d in ("data/vectordb", "data/sqlite", "data/models", "data/uploads"):
        (DIST_DIR / d).mkdir(parents=True, exist_ok=True)

    # Create launcher script
    launcher = DIST_DIR / "start_backend.py"
    launcher.write_text('''\
"""Launch the SRA backend server."""
import sys
import os

# Add this directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000)
''')

    # Create Windows batch launcher
    (DIST_DIR / "start.bat").write_text(
        '@echo off\r\necho Starting SRA Backend...\r\npython start_backend.py\r\npause\r\n'
    )

    # Create Linux shell launcher
    sh = DIST_DIR / "start.sh"
    sh.write_text('#!/bin/bash\necho "Starting SRA Backend..."\npython3 start_backend.py\n')
    sh.chmod(0o755)

    # Export requirements
    subprocess.run(
        [sys.executable, "-m", "pip", "freeze"],
        stdout=open(DIST_DIR / "requirements.txt", "w"),
        cwd=str(PROJECT_ROOT),
    )

    print(f"Backend package built: {DIST_DIR}")
    print(f"  Size: {sum(f.stat().st_size for f in DIST_DIR.rglob('*') if f.is_file()) / 1024 / 1024:.1f} MB")
    return DIST_DIR


if __name__ == "__main__":
    build()
