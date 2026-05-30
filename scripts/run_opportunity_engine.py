"""Run the research-only opportunity qualification engine."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.opportunity_engine.service import OpportunityService  # noqa: E402


def main() -> None:
    result = OpportunityService(PROJECT_ROOT).run()
    summary = result.analytics["summary"]
    print(
        {
            "opportunity_count": summary["opportunity_count"],
            "highest_score": summary["highest_score"],
            "average_score": summary["average_score"],
            "reports": result.report_paths,
        }
    )


if __name__ == "__main__":
    main()
