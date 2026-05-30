"""Run the market regime research layer."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.market_regime.service import MarketRegimeService  # noqa: E402


def main() -> None:
    """Run market regime service and print report paths."""
    run = MarketRegimeService(PROJECT_ROOT).run()
    print(
        {
            "regime": run.result.regime.regime_state,
            "score": run.result.regime.regime_score,
            "compatibility": run.result.compatibility.score,
            "reports": run.report_paths,
            "research_only": True,
        }
    )


if __name__ == "__main__":
    main()
