"""Run the research-only signal stream engine."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.signal_stream.service import SignalStreamService  # noqa: E402


def main() -> None:
    """Run signal stream service and print report paths."""
    run = SignalStreamService(PROJECT_ROOT).run()
    print(
        {
            "score": run.result.scoring.score,
            "state": run.result.scoring.state,
            "reports": run.report_paths,
            "research_only": True,
            "signal_generation_only": True,
        }
    )


if __name__ == "__main__":
    main()
