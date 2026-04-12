"""Final verification checklist — run all checks before delivery."""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHECKS: list[tuple[str, bool]] = []


def check(name: str, passed: bool) -> None:
    CHECKS.append((name, passed))
    icon = "PASS" if passed else "FAIL"
    print(f"  [{icon}] {name}")


def run_cmd(cmd: list[str], cwd: str | None = None, timeout: int = 120) -> tuple[int, str]:
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=cwd or str(PROJECT_ROOT), timeout=timeout,
        )
        return result.returncode, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return -1, "TIMEOUT"
    except FileNotFoundError:
        return -1, "COMMAND NOT FOUND"


def main() -> None:
    print("=" * 60)
    print("  SRA v0.1.0 — Final Verification Report")
    print("=" * 60)
    print()

    # 1. Unit tests
    print("--- Python Tests ---")
    code, out = run_cmd([sys.executable, "-m", "pytest", "tests/", "--tb=no", "-q"])
    passed_line = [l for l in out.split("\n") if "passed" in l]
    check("Python unit tests", code == 0 and "failed" not in out.lower())
    if passed_line:
        print(f"    {passed_line[-1].strip()}")

    # 2. Frontend build
    print("\n--- Frontend Build ---")
    code, out = run_cmd(["npx", "tsc", "-b", "--noEmit"], cwd=str(PROJECT_ROOT / "frontend"))
    check("TypeScript compilation", code == 0)

    code, out = run_cmd(["npx", "vite", "build"], cwd=str(PROJECT_ROOT / "frontend"))
    check("Vite production build", code == 0 and "built in" in out.lower())

    # 3. Documentation
    print("\n--- Documentation ---")
    docs = [
        "docs/user_guide.md", "docs/admin_guide.md", "docs/security_review.md",
        "docs/performance_report.md", "RELEASE_NOTES.md",
        "docs/handover/technical_overview.md", "docs/handover/test_report.md",
        "docs/handover/deployment_guide.md", "docs/handover/future_roadmap.md",
        "docs/handover/known_limitations.md", "docs/handover/demo_script.md",
    ]
    for doc in docs:
        path = PROJECT_ROOT / doc
        exists = path.exists() and path.stat().st_size > 100
        check(f"Documentation: {doc}", exists)

    # 4. Key source files
    print("\n--- Key Source Files ---")
    key_files = [
        "backend/main.py", "backend/config.py", "core/rag/engine.py",
        "core/validation/pipeline.py", "core/conversation/manager.py",
        "core/ingest/pipeline.py", "core/architecture/extractor.py",
        "core/reports/generator.py", "core/profile/tracker.py",
        "frontend/src/App.tsx", "frontend/src/pages/ChatPage.tsx",
    ]
    for f in key_files:
        check(f"Source: {f}", (PROJECT_ROOT / f).exists())

    # 5. Git status
    print("\n--- Repository ---")
    code, out = run_cmd(["git", "status", "--porcelain"])
    check("Git working tree clean", code == 0 and out.strip() == "")

    # Summary
    print("\n" + "=" * 60)
    total = len(CHECKS)
    passed = sum(1 for _, ok in CHECKS if ok)
    failed = total - passed

    if failed == 0:
        print(f"  READY FOR DELIVERY — {passed}/{total} checks passed")
    else:
        print(f"  NOT READY — {failed} checks failed, {passed}/{total} passed")
        print("\n  Failed checks:")
        for name, ok in CHECKS:
            if not ok:
                print(f"    - {name}")
    print("=" * 60)

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
