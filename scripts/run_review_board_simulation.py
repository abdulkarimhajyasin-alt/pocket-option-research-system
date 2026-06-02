"""Run review board simulation generation."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.review_board_simulation.service import ReviewBoardSimulationService  # noqa: E402


def main() -> None:
    """Generate local review board simulation artifacts."""
    run = ReviewBoardSimulationService(PROJECT_ROOT).run_full_review_board_simulation()
    print(
        {
            "simulation_status": run.summary["simulation_status"],
            "simulation_only": run.summary["simulation_only"],
            "review_only": run.summary["review_only"],
            "dry_run_only": run.summary["dry_run_only"],
            "overall_review_readiness_score": run.summary[
                "overall_review_readiness_score"
            ],
            "diagnostics": len(run.diagnostics),
            "storage": run.storage_paths,
            "reports": run.report_paths,
        }
    )


if __name__ == "__main__":
    main()
