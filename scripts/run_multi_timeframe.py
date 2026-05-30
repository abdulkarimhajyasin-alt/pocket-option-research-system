"""Run the research-only multi-timeframe confirmation engine."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.multi_timeframe.service import MultiTimeframeService  # noqa: E402


def main() -> None:
    result = MultiTimeframeService(PROJECT_ROOT).run()
    summary = result.analytics["summary"]
    print(
        {
            "confirmed_count": summary["confirmed_count"],
            "conflicting_count": summary["conflicting_count"],
            "average_alignment": summary["average_alignment"],
            "reports": result.report_paths,
        }
    )


if __name__ == "__main__":
    main()
