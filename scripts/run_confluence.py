"""Run the confluence research layer and generate reports."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.confluence.service import ConfluenceService  # noqa: E402


def main() -> None:
    result = ConfluenceService(PROJECT_ROOT).run()
    summary = result.analytics.get("summary", {})
    print(
        {
            "confluent_count": summary.get("confluent_count", 0),
            "average_confluence": summary.get("average_confluence", 0.0),
            "strong_count": summary.get("strong_count", 0),
            "reports": result.report_paths,
        }
    )


if __name__ == "__main__":
    main()
