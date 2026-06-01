"""Run trading requirements and constraints specification generation."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.trading_requirements.service import TradingRequirementsService  # noqa: E402


def main() -> None:
    """Generate local requirements-only artifacts."""
    run = TradingRequirementsService(PROJECT_ROOT).run_full_requirements_specification()
    print(
        {
            "requirements_status": run.summary["requirements_status"],
            "go_no_go_state": run.summary["go_no_go_state"],
            "requirements_only": run.summary["requirements_only"],
            "architecture_only": run.summary["architecture_only"],
            "diagnostics": len(run.diagnostics),
            "storage": run.storage_paths,
            "reports": run.report_paths,
        }
    )


if __name__ == "__main__":
    main()
