"""Run the readiness-only paper-to-live gate."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.paper_live_readiness.service import PaperToLiveReadinessService  # noqa: E402


def main() -> None:
    """Generate paper-to-live readiness storage and reports."""
    service = PaperToLiveReadinessService(PROJECT_ROOT)
    run = service.run()
    readiness = run.result.readiness
    print("Paper-to-live readiness gate generated")
    print(f"overall_score={readiness.overall_score}")
    print(f"readiness_state={readiness.readiness_state}")
    print(f"safety_score={readiness.safety_score}")
    print("readiness_only=True")
    print("paper_only=True")
    print("research_only=True")
    print("not_live_trading=True")
    print("not_broker_access=True")
    print(f"storage={run.storage_paths}")
    print(f"reports={run.report_paths}")


if __name__ == "__main__":
    main()
