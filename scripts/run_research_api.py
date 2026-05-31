"""Run the unified local research API materialization."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.research_api.service import UnifiedResearchAPIService  # noqa: E402


def main() -> None:
    """Generate unified research API storage and reports."""
    run = UnifiedResearchAPIService(PROJECT_ROOT).run()
    snapshot = run.snapshot.to_dict()
    print("Unified research API generated")
    print(f"snapshot_id={snapshot['snapshot_id']}")
    print(f"schema_version={snapshot['metadata']['schema_version']}")
    print("research_only=True")
    print("local_only=True")
    print("not_execution=True")
    print("not_broker_access=True")
    print("not_browser_automation=True")
    print(f"storage={run.storage_paths}")
    print(f"reports={run.report_paths}")


if __name__ == "__main__":
    main()
