"""Run the local research archive and versioning cycle."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.research_archive.service import ResearchArchiveService  # noqa: E402


def main() -> None:
    """Build the current archive snapshot, version, diff, and evolution reports."""
    result = ResearchArchiveService(PROJECT_ROOT).run_full_archive_cycle()
    print(
        {
            "version": result.version.version_label,
            "snapshot_id": result.snapshot.snapshot_id,
            "checksum": result.snapshot.checksum,
            "research_only": result.snapshot.research_only,
            "diagnostics": len(result.diagnostics),
            "reports": result.report_paths,
        }
    )


if __name__ == "__main__":
    main()
