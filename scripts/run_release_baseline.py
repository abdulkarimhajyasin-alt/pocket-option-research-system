"""Run release baseline reconciliation generation."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.release_baseline.service import ReleaseBaselineService  # noqa: E402


def main() -> None:
    """Generate local non-destructive release baseline artifacts."""
    run = ReleaseBaselineService(PROJECT_ROOT).run_full_release_baseline()
    print(
        {
            "baseline_state": run.summary["baseline_state"],
            "baseline_reconciliation_only": run.summary["baseline_reconciliation_only"],
            "manual_cleanup_planning_only": run.summary["manual_cleanup_planning_only"],
            "non_destructive": run.summary["non_destructive"],
            "overall_baseline_readiness_score": run.summary[
                "overall_baseline_readiness_score"
            ],
            "diagnostics": len(run.diagnostics),
            "storage": run.storage_paths,
            "reports": run.report_paths,
        }
    )


if __name__ == "__main__":
    main()
