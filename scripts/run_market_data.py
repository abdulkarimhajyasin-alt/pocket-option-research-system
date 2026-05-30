"""Run the research-only market data integration cycle."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.market_data.service import MarketDataService  # noqa: E402


def main() -> None:
    """Collect static research market data and export reports."""
    result = MarketDataService(PROJECT_ROOT).run()
    summary = result.analytics["summary"]
    print(
        {
            "asset_count": summary["asset_count"],
            "market_status": summary["market_status"],
            "provider_health": summary["provider_health"],
            "readiness_score": summary["readiness_score"],
            "reports": result.report_paths,
        }
    )


if __name__ == "__main__":
    main()
