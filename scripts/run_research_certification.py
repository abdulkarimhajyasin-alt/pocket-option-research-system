"""Run the research certification layer."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.research_certification.service import ResearchCertificationService  # noqa: E402


def main() -> None:
    """Run certification service and print report paths."""
    run = ResearchCertificationService(PROJECT_ROOT).run()
    print(
        {
            "score": run.result.certification.score,
            "state": run.result.certification.state,
            "reports": run.report_paths,
            "research_only": True,
        }
    )


if __name__ == "__main__":
    main()
