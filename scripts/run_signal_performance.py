"""Run the research-only signal performance validation cycle."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.signal_performance.service import SignalPerformanceService  # noqa: E402


def main() -> None:
    result = SignalPerformanceService(PROJECT_ROOT).run()
    summary = result.analytics["summary"]
    print(
        {
            "total_signals": summary["total_signals"],
            "wins": summary["wins"],
            "losses": summary["losses"],
            "win_rate": summary["win_rate"],
            "readiness": summary["readiness_label"],
            "reports": result.report_paths,
        }
    )


if __name__ == "__main__":
    main()
