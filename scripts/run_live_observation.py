"""Run the deterministic live observation replay engine."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.live_observation.service import LiveObservationService  # noqa: E402


def main() -> None:
    """Run the replay service and print report paths."""
    run = LiveObservationService(PROJECT_ROOT).run()
    print(
        {
            "score": run.result.replay.score,
            "state": run.result.state.state,
            "reports": run.report_paths,
            "research_only": True,
            "observation_only": True,
            "live_observation_replay": True,
        }
    )


if __name__ == "__main__":
    main()
