"""Run governance traceability generation."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.governance_traceability.service import GovernanceTraceabilityService  # noqa: E402


def main() -> None:
    """Generate local traceability mapping artifacts."""
    run = GovernanceTraceabilityService(PROJECT_ROOT).run_full_governance_traceability()
    print(
        {
            "traceability_status": run.summary["traceability_status"],
            "readiness_state": run.summary["readiness_state"],
            "traceability_only": run.summary["traceability_only"],
            "governance_only": run.summary["governance_only"],
            "overall_traceability_score": run.summary["overall_traceability_score"],
            "diagnostics": len(run.diagnostics),
            "storage": run.storage_paths,
            "reports": run.report_paths,
        }
    )


if __name__ == "__main__":
    main()
