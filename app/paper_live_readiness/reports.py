"""Report writer for paper-to-live readiness."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.paper_live_readiness.models import PaperToLiveReadinessRun


class PaperToLiveReadinessReportWriter:
    """Write readiness reports."""

    def __init__(self, output_dir: Path | str = "reports/paper_live_readiness") -> None:
        self.output_dir = Path(output_dir)

    def export(self, result: PaperToLiveReadinessRun) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "summary": self.output_dir / "readiness_summary.json",
            "gates": self.output_dir / "gate_report.json",
            "safety": self.output_dir / "safety_report.json",
            "maturity": self.output_dir / "maturity_report.json",
            "stability": self.output_dir / "stability_report.json",
            "diagnostics": self.output_dir / "diagnostics_report.json",
            "recommendations": self.output_dir / "recommendations_report.json",
        }
        self._write(
            paths["summary"],
            {"summary": result.readiness.to_dict(), "latest": result.to_dict()},
        )
        self._write(paths["gates"], self._count(item.status for item in result.gates))
        self._write(paths["safety"], result.safety)
        self._write(paths["maturity"], result.maturity)
        self._write(paths["stability"], result.stability)
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
