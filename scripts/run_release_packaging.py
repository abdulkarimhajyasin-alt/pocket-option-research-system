"""Run final repository stabilization and release packaging."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.release_packaging.service import ReleasePackagingService  # noqa: E402


def main() -> None:
    """Generate Research Platform v1.0 release package outputs."""
    run = ReleasePackagingService(PROJECT_ROOT).run_full_release_packaging()
    print(
        {
            "release_id": run.manifest["release_id"],
            "release_status": run.manifest["release_status"],
            "recommended_next_decision": run.project_status["recommended_next_decision"],
            "diagnostics": len(run.diagnostics),
            "storage": run.storage_paths,
            "reports": run.report_paths,
        }
    )


if __name__ == "__main__":
    main()
