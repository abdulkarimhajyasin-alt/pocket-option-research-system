"""Run production system design blueprint generation."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.production_system_design.service import ProductionSystemDesignService  # noqa: E402


def main() -> None:
    """Generate local design-only production blueprint artifacts."""
    run = ProductionSystemDesignService(PROJECT_ROOT).run_full_production_design()
    print(
        {
            "design_status": run.summary["design_status"],
            "readiness_state": run.summary["readiness_state"],
            "design_only": run.summary["design_only"],
            "architecture_only": run.summary["architecture_only"],
            "diagnostics": len(run.diagnostics),
            "storage": run.storage_paths,
            "reports": run.report_paths,
        }
    )


if __name__ == "__main__":
    main()
