"""Master build script — assembles the full offline installer package."""

import hashlib
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VERSION = "0.1.0"
RELEASE_DIR = PROJECT_ROOT / "release"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def build_release() -> Path:
    """Build the full release package."""
    print(f"=== Building SRA Release v{VERSION} ===")
    print(f"Platform: {platform.system()} {platform.machine()}")

    if RELEASE_DIR.exists():
        shutil.rmtree(RELEASE_DIR)

    os_name = "windows" if platform.system() == "Windows" else "linux"
    arch = "x64"
    pkg_name = f"SecurityResearchAssistant-{VERSION}-{os_name}-{arch}"
    pkg_dir = RELEASE_DIR / pkg_name

    # 1. Build backend
    print("\n--- Building backend ---")
    from scripts.build_backend import build as build_backend
    backend_dist = build_backend()

    # Copy backend to package
    shutil.copytree(backend_dist, pkg_dir / "backend")

    # 2. Copy config and docs
    print("\n--- Copying configuration and docs ---")
    for f in ("config.yaml",):
        src = PROJECT_ROOT / "security-research-assistant" / f if not (PROJECT_ROOT / f).exists() else PROJECT_ROOT / f
        if src.exists():
            shutil.copy2(src, pkg_dir / f)
    if (PROJECT_ROOT / "config.yaml").exists():
        shutil.copy2(PROJECT_ROOT / "config.yaml", pkg_dir / "config.yaml")

    # Copy docs
    docs_src = PROJECT_ROOT / "docs"
    if docs_src.exists():
        shutil.copytree(docs_src, pkg_dir / "docs")

    # 3. Create launcher
    shutil.copy2(PROJECT_ROOT / "scripts" / "launcher.py", pkg_dir / "launcher.py")

    # 4. Create README
    readme = pkg_dir / "README.txt"
    readme.write_text(f"""Security Research Assistant v{VERSION}
{'=' * 45}

Quick Start:
1. Ensure Ollama is installed and has a model available
   (ollama pull mistral:7b-instruct-v0.3-q4_K_M)
2. Run: python launcher.py
3. Open the desktop application or navigate to http://localhost:8000/docs

For full documentation, see docs/user_guide.md

This tool operates fully offline. No internet connection required.
""")

    # 5. Create install instructions
    if os_name == "windows":
        (pkg_dir / "INSTALL.txt").write_text(f"""Installation Instructions — Windows
{'=' * 40}
1. Extract this archive to a location of your choice
2. Install Ollama from the bundled installer or https://ollama.com
3. Open a terminal and run: ollama pull mistral:7b-instruct-v0.3-q4_K_M
4. Run launcher.py to start all services
5. Open the application
""")
    else:
        install_sh = pkg_dir / "install.sh"
        install_sh.write_text("""#!/bin/bash
echo "Installing Security Research Assistant..."
chmod +x launcher.py backend/start.sh
echo "Installation complete. Run: python3 launcher.py"
""")
        install_sh.chmod(0o755)

    # 6. Generate checksums
    print("\n--- Generating checksums ---")
    checksums = []
    for f in sorted(pkg_dir.rglob("*")):
        if f.is_file():
            rel = f.relative_to(pkg_dir)
            h = sha256_file(f)
            checksums.append(f"{h}  {rel}")

    (pkg_dir / "checksums.sha256").write_text("\n".join(checksums) + "\n")

    # 7. Create archive
    print("\n--- Creating archive ---")
    if os_name == "windows":
        archive = shutil.make_archive(str(RELEASE_DIR / pkg_name), "zip", str(RELEASE_DIR), pkg_name)
    else:
        archive = shutil.make_archive(str(RELEASE_DIR / pkg_name), "gztar", str(RELEASE_DIR), pkg_name)

    print(f"\n=== Release built ===")
    print(f"Package: {archive}")
    archive_path = Path(archive)
    print(f"Size: {archive_path.stat().st_size / 1024 / 1024:.1f} MB")
    print(f"Checksum: {sha256_file(archive_path)}")

    return archive_path


if __name__ == "__main__":
    build_release()
