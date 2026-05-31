"""Reports for paper control center."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.paper_control_center.models import PaperControlCenterRun


class PaperControlReportWriter:
    """Write paper control center reports."""

    def __init__(self, output_dir: Path | str = "reports/paper_control_center") -> None:
        self.output_dir = Path(output_dir)

    def export(self, result: PaperControlCenterRun) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "summary": self.output_dir / "control_center_summary.json",
            "health": self.output_dir / "health_report.json",
            "monitoring": self.output_dir / "monitoring_report.json",
            "governance": self.output_dir / "governance_report.json",
            "decision": self.output_dir / "decision_report.json",
            "analytics": self.output_dir / "analytics_report.json",
            "diagnostics": self.output_dir / "diagnostics_report.json",
            "recommendations": self.output_dir / "recommendations_report.json",
        }
        self._write(
            paths["summary"],
            {"summary": result.control.to_dict(), "latest": result.to_dict()},
        )
        self._write(paths["health"], result.health)
        self._write(paths["monitoring"], result.monitoring)
        self._write(paths["governance"], self._count(item.status for item in result.governance))
        self._write(paths["decision"], result.decision)
        self._write(paths["analytics"], result.analytics)
        self._write(paths["diagnostics"], self._count(item.name for item in result.diagnostics))
        self._write(
            paths["recommendations"],
            self._count(item.title for item in result.recommendations),
        )
        return {key: str(path) for key, path in paths.items()}

    def _count(self, values: Any) -> dict[str, int]:
        counts: dict[str, int] = {}
        for value in values:
            key = str(value)
            counts[key] = counts.get(key, 0) + 1
        return counts

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
