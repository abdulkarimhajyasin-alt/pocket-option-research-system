"""Run the paper-only trading control center."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.paper_control_center.service import PaperControlCenterService  # noqa: E402


def main() -> None:
    """Generate paper control center storage and reports."""
    run = PaperControlCenterService(PROJECT_ROOT).run()
    control = run.result.control
    print("Paper control center generated")
    print(f"overall_score={control.overall_score}")
    print(f"governance_status={control.governance_status}")
    print(f"warning_count={control.warning_count}")
    print(f"recommendation_count={control.recommendation_count}")
    print("paper_only=True")
    print("research_only=True")
    print("recommendation_only=True")
    print(f"storage={run.storage_paths}")
    print(f"reports={run.report_paths}")


if __name__ == "__main__":
    main()
