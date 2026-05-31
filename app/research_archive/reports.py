"""Report writer for research archive outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ResearchArchiveReportWriter:
    """Write dashboard-friendly archive reports."""

    def __init__(self, output_dir: Path | str = "reports/research_archive") -> None:
        self.output_dir = Path(output_dir)

    def export(
        self,
        summary: dict[str, Any],
        versions: list[dict[str, Any]],
        latest: dict[str, Any],
        diff: dict[str, Any],
        evolution: dict[str, Any],
        diagnostics: list[dict[str, Any]],
        recommendations: list[str],
    ) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "summary": self.output_dir / "archive_summary.json",
            "history": self.output_dir / "version_history.json",
            "latest": self.output_dir / "latest_version_report.json",
            "diff": self.output_dir / "diff_report.json",
            "evolution": self.output_dir / "evolution_report.json",
            "diagnostics": self.output_dir / "diagnostics_report.json",
            "recommendations": self.output_dir / "recommendations_report.json",
        }
        self._write(paths["summary"], summary)
        self._write(paths["history"], versions)
        self._write(paths["latest"], latest)
        self._write(paths["diff"], diff)
        self._write(paths["evolution"], evolution)
        self._write(paths["diagnostics"], diagnostics)
        self._write(paths["recommendations"], {"items": recommendations, "research_only": True})
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
