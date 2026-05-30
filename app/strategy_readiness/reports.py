"""Deterministic reports for strategy readiness."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class StrategyReadinessReportWriter:
    """Write readiness reports for dashboard and audit use."""

    def __init__(self, output_dir: Path | str = "reports/strategy_readiness") -> None:
        self.output_dir = Path(output_dir)

    def export(self, analytics: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "summary": self.output_dir / "readiness_summary.json",
            "gates": self.output_dir / "gate_analysis.json",
            "diagnostics": self.output_dir / "diagnostics_report.json",
            "recommendations": self.output_dir / "recommendations_report.json",
            "stability": self.output_dir / "stability_report.json",
            "failure": self.output_dir / "failure_analysis.json",
        }
        self._write(
            paths["summary"],
            {
                "summary": analytics.get("summary", {}),
                "readiness_distribution": analytics.get("readiness_distribution", {}),
                "strengths": analytics.get("strengths", {}),
                "weaknesses": analytics.get("weaknesses", {}),
                "timeline": analytics.get("timeline", {}),
                "latest": analytics.get("latest", {}),
            },
        )
        self._write(paths["gates"], analytics.get("gate_distribution", {}))
        self._write(paths["diagnostics"], analytics.get("diagnostics_analysis", {}))
        self._write(
            paths["recommendations"],
            analytics.get("recommendation_distribution", {}),
        )
        self._write(paths["stability"], analytics.get("stability_analysis", {}))
        self._write(paths["failure"], analytics.get("failure_distribution", {}))
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
