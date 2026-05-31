"""Report writer for execution readiness."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ExecutionReadinessReportWriter:
    """Write dashboard reports for execution readiness."""

    def __init__(self, output_dir: Path | str = "reports/execution_readiness") -> None:
        self.output_dir = Path(output_dir)

    def export(self, analytics: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        latest = analytics.get("latest", {})
        paths = {
            "summary": self.output_dir / "execution_summary.json",
            "readiness": self.output_dir / "readiness_report.json",
            "qualification": self.output_dir / "qualification_report.json",
            "gate": self.output_dir / "gate_report.json",
            "validation": self.output_dir / "validation_report.json",
            "diagnostics": self.output_dir / "diagnostics_report.json",
            "recommendations": self.output_dir / "recommendations_report.json",
        }
        self._write(paths["summary"], {"summary": analytics.get("summary", {}), "latest": latest})
        self._write(paths["readiness"], analytics.get("readiness_distribution", {}))
        self._write(paths["qualification"], analytics.get("qualification_distribution", {}))
        self._write(paths["gate"], analytics.get("gate_distribution", {}))
        self._write(paths["validation"], latest.get("validation", {}))
        self._write(paths["diagnostics"], analytics.get("warning_distribution", {}))
        self._write(paths["recommendations"], analytics.get("recommendation_distribution", {}))
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
