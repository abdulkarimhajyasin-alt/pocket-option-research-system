"""Run the local paper-only execution engine."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.paper_execution.service import PaperExecutionService  # noqa: E402


def main() -> None:
    """Generate paper execution storage and reports."""
    run = PaperExecutionService(PROJECT_ROOT).run()
    summary = run.result.analytics
    print("Paper execution generated")
    print(f"paper_orders={summary['total_paper_orders']}")
    print(f"accepted={summary['accepted']}")
    print(f"rejected={summary['rejected']}")
    print(f"paper_execution_score={summary['paper_execution_score']}")
    print("paper_only=True")
    print("research_only=True")
    print("not_real_execution=True")
    print(f"storage={run.storage_paths}")
    print(f"reports={run.report_paths}")


if __name__ == "__main__":
    main()
