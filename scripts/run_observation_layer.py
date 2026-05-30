"""Run the offline broker observation layer and export reports."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.observation.service import ObservationService  # noqa: E402


def main() -> None:
    """Collect mock observations and write local research artifacts."""
    result = ObservationService(PROJECT_ROOT).run()
    print(
        {
            "active_assets": result.analytics["active_assets"],
            "average_payout": result.analytics["average_payout"],
            "market_activity_score": result.analytics["market_activity_score"],
            "observation_count": result.analytics["observation_count"],
            "reports": result.report_paths,
        }
    )


if __name__ == "__main__":
    main()
