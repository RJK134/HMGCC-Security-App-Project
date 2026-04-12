"""Application launcher — manages Ollama and backend lifecycle.

Starts Ollama (if not running), starts the backend, monitors health,
and handles graceful shutdown.
"""

import atexit
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class SRALauncher:
    """Manage the SRA application services."""

    def __init__(self) -> None:
        self._backend_proc: subprocess.Popen | None = None
        self._ollama_proc: subprocess.Popen | None = None
        self._ollama_was_running = False

    def start(self) -> bool:
        """Start all services. Returns True if backend is healthy."""
        print("=== SRA Launcher ===")

        # 1. Check/start Ollama
        self._start_ollama()

        # 2. Start backend
        if not self._start_backend():
            print("[ERROR] Backend failed to start.")
            return False

        print("[OK] All services running.")
        print("     Backend: http://localhost:8000")
        print("     API docs: http://localhost:8000/docs")
        print("     Health: http://localhost:8000/api/v1/health")
        return True

    def stop(self) -> None:
        """Gracefully stop all services."""
        print("Shutting down...")
        if self._backend_proc and self._backend_proc.poll() is None:
            self._backend_proc.terminate()
            self._backend_proc.wait(timeout=10)
            print("[OK] Backend stopped.")

        if self._ollama_proc and not self._ollama_was_running:
            self._ollama_proc.terminate()
            print("[OK] Ollama stopped.")

    def _start_ollama(self) -> None:
        """Ensure Ollama is running."""
        if self._check_ollama():
            print("[OK] Ollama already running.")
            self._ollama_was_running = True
            return

        print("[..] Starting Ollama...")
        try:
            self._ollama_proc = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            for _ in range(30):
                time.sleep(1)
                if self._check_ollama():
                    print("[OK] Ollama started.")
                    return
            print("[!!] Ollama did not start within 30 seconds.")
        except FileNotFoundError:
            print("[!!] Ollama not found. LLM features will be unavailable.")
            print("     Install Ollama from: https://ollama.com")

    def _start_backend(self) -> bool:
        """Start the FastAPI backend."""
        print("[..] Starting backend...")
        self._backend_proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend.main:app",
             "--host", "127.0.0.1", "--port", "8000"],
            cwd=str(PROJECT_ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        for _ in range(15):
            time.sleep(1)
            if self._check_backend():
                print("[OK] Backend started.")
                return True

        return False

    def _check_ollama(self) -> bool:
        try:
            urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2)
            return True
        except Exception:
            return False

    def _check_backend(self) -> bool:
        try:
            urllib.request.urlopen("http://localhost:8000/api/v1/health", timeout=2)
            return True
        except Exception:
            return False


def main() -> None:
    launcher = SRALauncher()
    atexit.register(launcher.stop)

    if not launcher.start():
        print("Failed to start services. Check logs for details.")
        sys.exit(1)

    print("\nPress Ctrl+C to stop all services.\n")
    try:
        while True:
            time.sleep(5)
            if not launcher._check_backend():
                print("[!!] Backend appears to have stopped. Attempting restart...")
                launcher._start_backend()
    except KeyboardInterrupt:
        print()
        launcher.stop()


if __name__ == "__main__":
    main()
