"""Run control assurance generation."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.control_assurance.service import ControlAssuranceService  # noqa: E402


def main() -> None:
    """Generate local assurance artifacts."""
    run = ControlAssuranceService(PROJECT_ROOT).run_full_control_assurance()
    print(
        {
            "assurance_status": run.summary["assurance_status"],
            "review_readiness_state": run.summary["review_readiness_state"],
            "assurance_only": run.summary["assurance_only"],
            "review_readiness_only": run.summary["review_readiness_only"],
            "overall_assurance_score": run.summary["overall_assurance_score"],
            "diagnostics": len(run.diagnostics),
            "storage": run.storage_paths,
            "reports": run.report_paths,
        }
    )


if __name__ == "__main__":
    main()
