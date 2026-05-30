"""Run the strategy benchmark research layer."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.strategy_benchmark.service import StrategyBenchmarkService  # noqa: E402


def main() -> None:
    """Run strategy benchmark service and print report paths."""
    run = StrategyBenchmarkService(PROJECT_ROOT).run()
    print(
        {
            "profiles": len(run.result.comparisons),
            "best_profile": run.analytics["summary"]["best_profile"],
            "highest_score": run.analytics["summary"]["highest_score"],
            "reports": run.report_paths,
            "research_only": True,
        }
    )


if __name__ == "__main__":
    main()
