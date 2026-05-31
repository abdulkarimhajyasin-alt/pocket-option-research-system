"""Run the read-only browser observation adapter."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.browser_observation.service import BrowserObservationService  # noqa: E402


def main() -> None:
    """Run browser observation service and print report paths."""
    run = BrowserObservationService(PROJECT_ROOT).run()
    print(
        {
            "score": run.result.adapter.score,
            "state": run.result.adapter.state,
            "reports": run.report_paths,
            "research_only": True,
            "observation_only": True,
            "read_only": True,
        }
    )


if __name__ == "__main__":
    main()
