"""Run the adaptive pattern memory research layer."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.pattern_memory.service import PatternMemoryService  # noqa: E402


def main() -> None:
    """Run pattern memory service and print report paths."""
    run = PatternMemoryService(PROJECT_ROOT).run()
    print(
        {
            "patterns": len(run.result.records),
            "discovered": len(run.result.discovered_patterns),
            "best_pattern": run.analytics["summary"]["best_pattern"],
            "reports": run.report_paths,
            "research_only": True,
        }
    )


if __name__ == "__main__":
    main()
