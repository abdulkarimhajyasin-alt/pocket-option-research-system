"""Run the research-only signal intelligence engine."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.signal_intelligence.service import SignalIntelligenceService  # noqa: E402


def main() -> None:
    result = SignalIntelligenceService(PROJECT_ROOT).run()
    summary = result.analytics["summary"]
    print(
        {
            "signal_count": summary["signal_count"],
            "average_confidence": summary["average_confidence"],
            "highest_confidence": summary["highest_confidence"],
            "reports": result.report_paths,
        }
    )


if __name__ == "__main__":
    main()
