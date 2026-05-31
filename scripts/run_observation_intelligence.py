"""Run the unified observation intelligence layer."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.observation_intelligence.service import ObservationIntelligenceService  # noqa: E402


def main() -> None:
    """Run observation intelligence service and print report paths."""
    run = ObservationIntelligenceService(PROJECT_ROOT).run()
    print(
        {
            "score": run.result.intelligence.score,
            "state": run.result.intelligence.state,
            "reports": run.report_paths,
            "research_only": True,
            "observation_only": True,
        }
    )


if __name__ == "__main__":
    main()
