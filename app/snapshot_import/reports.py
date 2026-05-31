"""Reports for manual snapshot imports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class SnapshotImportReportWriter:
    """Write deterministic manual snapshot import reports."""

    def __init__(self, output_dir: Path | str = "reports/snapshot_import") -> None:
        self.output_dir = Path(output_dir)

    def export(self, analytics: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "summary": self.output_dir / "import_summary.json",
            "validation": self.output_dir / "validation_report.json",
            "processing": self.output_dir / "processing_report.json",
            "quality": self.output_dir / "quality_report.json",
            "diagnostics": self.output_dir / "diagnostics_report.json",
            "recommendations": self.output_dir / "recommendations_report.json",
        }
        self._write(
            paths["summary"],
            {
                "summary": analytics.get("summary", {}),
                "import_distribution": analytics.get("import_distribution", {}),
                "quality_timeline": analytics.get("quality_timeline", {}),
                "latest": analytics.get("latest", {}),
            },
        )
        self._write(paths["validation"], analytics.get("validation_distribution", {}))
        self._write(paths["processing"], analytics.get("processing_distribution", {}))
        self._write(paths["quality"], analytics.get("quality_distribution", {}))
        self._write(paths["diagnostics"], analytics.get("diagnostics_distribution", {}))
        self._write(
            paths["recommendations"],
            analytics.get("recommendation_distribution", {}),
        )
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
