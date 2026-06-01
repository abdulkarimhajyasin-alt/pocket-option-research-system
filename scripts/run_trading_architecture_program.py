"""Run Trading System Architecture Program foundation generation."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.trading_architecture_program.service import (  # noqa: E402
    TradingArchitectureProgramService,
)


def main() -> None:
    """Generate local architecture-only program artifacts."""
    run = TradingArchitectureProgramService(PROJECT_ROOT).run_full_program_foundation()
    print(
        {
            "program_name": run.summary["program_name"],
            "program_status": run.summary["program_status"],
            "architecture_only": run.summary["architecture_only"],
            "diagnostics": len(run.diagnostics),
            "storage": run.storage_paths,
            "reports": run.report_paths,
        }
    )


if __name__ == "__main__":
    main()
