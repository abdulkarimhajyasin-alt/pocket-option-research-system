"""Report writer for paper-only execution."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.paper_execution.models import PaperExecutionRun


class PaperExecutionReportWriter:
    """Write dashboard reports for paper execution."""

    def __init__(self, output_dir: Path | str = "reports/paper_execution") -> None:
        self.output_dir = Path(output_dir)

    def export(self, result: PaperExecutionRun) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "summary": self.output_dir / "paper_execution_summary.json",
            "orders": self.output_dir / "orders_report.json",
            "lifecycle": self.output_dir / "lifecycle_report.json",
            "results": self.output_dir / "results_report.json",
            "risk": self.output_dir / "risk_report.json",
            "analytics": self.output_dir / "analytics_report.json",
            "diagnostics": self.output_dir / "diagnostics_report.json",
            "recommendations": self.output_dir / "recommendations_report.json",
        }
        self._write(paths["summary"], {"summary": result.analytics, "latest": result.to_dict()})
        self._write(paths["orders"], self._count(item.status for item in result.orders))
        self._write(paths["lifecycle"], [item.to_dict() for item in result.lifecycle])
        self._write(paths["results"], self._count(item.outcome for item in result.results))
        self._write(paths["risk"], self._count(item.status for item in result.risk_gates))
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
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
