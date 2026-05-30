"""Run the research operations control center."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.research_ops.service import ResearchOperationsService  # noqa: E402


def main() -> None:
    run = ResearchOperationsService(PROJECT_ROOT).run()
    summary = run.analytics.get("summary", {})
    print(
        {
            "health_score": summary.get("health_score", 0.0),
            "readiness_score": summary.get("readiness_score", 0.0),
            "alert_count": summary.get("alert_count", 0),
            "recommendation_count": summary.get("recommendation_count", 0),
            "reports": run.report_paths,
        }
    )


if __name__ == "__main__":
    main()
