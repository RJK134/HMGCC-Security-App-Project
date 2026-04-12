"""Development startup script.

Checks Ollama availability, then starts the FastAPI backend server.
"""

import subprocess
import sys
from pathlib import Path

# Ensure we can import from the project root
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from backend.config import get_settings


def check_ollama(base_url: str) -> bool:
    """Check if Ollama is running and reachable.

    Args:
        base_url: Ollama server URL.

    Returns:
        True if Ollama responds.
    """
    try:
        import urllib.request
        urllib.request.urlopen(f"{base_url}/api/tags", timeout=3)
        return True
    except Exception:
        return False


def main() -> None:
    """Run preflight checks and start the backend server."""
    settings = get_settings()

    print("=" * 60)
    print("  Security Research Assistant — Development Server")
    print("=" * 60)
    print()

    # Check Ollama
    if check_ollama(settings.ollama_base_url):
        print(f"  [OK] Ollama running at {settings.ollama_base_url}")
    else:
        print(f"  [!!] Ollama NOT running at {settings.ollama_base_url}")
        print("       LLM features will be unavailable.")
        print("       Start Ollama with: ollama serve")
    print()

    print(f"  Model:     {settings.ollama_model}")
    print(f"  Embed:     {settings.ollama_embed_model}")
    print(f"  Database:  {settings.sqlite_path}")
    print(f"  Vectors:   {settings.chroma_path}")
    print()

    api_url = f"http://{settings.host}:{settings.port}"
    print(f"  Starting backend at {api_url}")
    print(f"  API docs:  {api_url}/docs")
    print(f"  Health:    {api_url}/api/v1/health")
    print()
    print("-" * 60)

    subprocess.run(
        [
            sys.executable, "-m", "uvicorn",
            "backend.main:app",
            "--host", settings.host,
            "--port", str(settings.port),
            "--reload",
        ],
        cwd=str(project_root),
    )


if __name__ == "__main__":
    main()
