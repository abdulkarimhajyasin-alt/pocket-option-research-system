"""Run the research-only execution readiness framework."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.execution_readiness.service import ExecutionReadinessService  # noqa: E402


def main() -> None:
    """Generate execution-readiness storage and reports."""
    run = ExecutionReadinessService(PROJECT_ROOT).run()
    summary = run.analytics["summary"]
    print("Execution readiness generated")
    print(f"candidates={summary['candidate_count']}")
    print(f"readiness_score={summary['average_readiness']}")
    print(f"qualification_state={summary['qualification_state']}")
    print("research_only=True")
    print("readiness_only=True")
    print("not_execution=True")
    print(f"storage={run.storage_paths}")
    print(f"reports={run.report_paths}")


if __name__ == "__main__":
    main()
