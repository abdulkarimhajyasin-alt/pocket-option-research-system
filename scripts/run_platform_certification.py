"""Run the final local research platform certification."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.platform_certification.service import PlatformCertificationService  # noqa: E402


def main() -> None:
    """Generate certification storage and report outputs."""
    run = PlatformCertificationService(PROJECT_ROOT).run()
    payload = run.certification.to_dict()
    print(
        {
            "certification_state": payload["certification_state"],
            "final_platform_score": payload["final_platform_score"],
            "research_only": payload["research_only"],
            "storage": run.storage_paths,
            "reports": run.report_paths,
        }
    )


if __name__ == "__main__":
    main()
