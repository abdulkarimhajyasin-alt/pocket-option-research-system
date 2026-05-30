"""Run the research-only trade lifecycle simulator."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.trade_lifecycle.service import TradeLifecycleService  # noqa: E402


def main() -> None:
    result = TradeLifecycleService(PROJECT_ROOT).run()
    summary = result.analytics.get("summary", {})
    print(
        {
            "total_lifecycles": summary.get("total_lifecycles", 0),
            "wins": summary.get("wins", 0),
            "losses": summary.get("losses", 0),
            "average_quality": summary.get("average_quality", 0.0),
            "reports": result.report_paths,
        }
    )


if __name__ == "__main__":
    main()
