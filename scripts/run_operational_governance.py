"""Run operational governance generation."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.operational_governance.service import OperationalGovernanceService  # noqa: E402


def main() -> None:
    """Generate local governance framework artifacts."""
    run = OperationalGovernanceService(PROJECT_ROOT).run_full_operational_governance()
    print(
        {
            "governance_status": run.summary["governance_status"],
            "readiness_state": run.summary["readiness_state"],
            "governance_only": run.summary["governance_only"],
            "design_only": run.summary["design_only"],
            "diagnostics": len(run.diagnostics),
            "storage": run.storage_paths,
            "reports": run.report_paths,
        }
    )


if __name__ == "__main__":
    main()
