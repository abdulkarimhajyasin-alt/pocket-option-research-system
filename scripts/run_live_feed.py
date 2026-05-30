"""Run the mock live market feed pipeline and export research reports."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.live_feed.service import LiveFeedService  # noqa: E402


def main() -> None:
    """Run one observation-only live-feed pipeline cycle."""
    result = LiveFeedService(PROJECT_ROOT).run()
    summary = result.analytics["summary"]
    print(
        {
            "health_label": summary["health_label"],
            "readiness": summary["readiness"],
            "active_assets": summary["active_assets"],
            "update_count": summary["update_count"],
            "reports": result.report_paths,
        }
    )


if __name__ == "__main__":
    main()
