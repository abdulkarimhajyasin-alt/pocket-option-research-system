"""Run the strategy readiness and gate framework."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.strategy_readiness.service import StrategyReadinessService  # noqa: E402


def main() -> None:
    result = StrategyReadinessService(PROJECT_ROOT).run()
    summary = result.analytics.get("summary", {})
    print(
        {
            "readiness_score": summary.get("readiness_score", 0.0),
            "readiness_state": summary.get("readiness_state", ""),
            "passed_gates": summary.get("passed_gates", 0),
            "failures": summary.get("failures", 0),
            "reports": result.report_paths,
        }
    )


if __name__ == "__main__":
    main()
