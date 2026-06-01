"""Run post-research strategic architecture artifact generation."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.post_research_architecture.service import PostResearchArchitectureService  # noqa: E402


def main() -> None:
    """Generate architecture-only post-research outputs."""
    run = PostResearchArchitectureService(PROJECT_ROOT).run_full_post_research_architecture()
    print(
        {
            "current_platform_state": run.summary["current_platform_state"],
            "recommended_future_program": run.summary["recommended_future_program"],
            "architecture_only": run.summary["architecture_only"],
            "research_only": run.summary["research_only"],
            "diagnostics": len(run.diagnostics),
            "storage": run.storage_paths,
            "reports": run.report_paths,
        }
    )


if __name__ == "__main__":
    main()
