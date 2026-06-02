"""Run repository hygiene artifact generation."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.repository_hygiene.service import RepositoryHygieneService  # noqa: E402


def main() -> None:
    """Generate local non-destructive repository hygiene artifacts."""
    run = RepositoryHygieneService(PROJECT_ROOT).run_full_repository_hygiene()
    print(
        {
            "hygiene_status": run.summary["hygiene_status"],
            "repository_hygiene_only": run.summary["repository_hygiene_only"],
            "artifact_policy_only": run.summary["artifact_policy_only"],
            "non_destructive": run.summary["non_destructive"],
            "overall_repository_hygiene_score": run.summary[
                "overall_repository_hygiene_score"
            ],
            "diagnostics": len(run.diagnostics),
            "storage": run.storage_paths,
            "reports": run.report_paths,
        }
    )


if __name__ == "__main__":
    main()
