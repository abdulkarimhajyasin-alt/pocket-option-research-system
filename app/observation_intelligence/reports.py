"""Reports for unified observation intelligence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ObservationIntelligenceReportWriter:
    """Write deterministic observation intelligence reports."""

    def __init__(self, output_dir: Path | str = "reports/observation_intelligence") -> None:
        self.output_dir = Path(output_dir)

    def export(self, analytics: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "summary": self.output_dir / "observation_summary.json",
            "quality": self.output_dir / "quality_report.json",
            "confidence": self.output_dir / "confidence_report.json",
            "validation": self.output_dir / "validation_report.json",
            "coverage": self.output_dir / "coverage_report.json",
            "diagnostics": self.output_dir / "diagnostics_report.json",
            "recommendations": self.output_dir / "recommendations_report.json",
        }
        self._write(
            paths["summary"],
            {
                "summary": analytics.get("summary", {}),
                "source_distribution": analytics.get("source_distribution", {}),
                "readiness_distribution": analytics.get("readiness_distribution", {}),
                "latest": analytics.get("latest", {}),
            },
        )
        self._write(paths["quality"], analytics.get("quality_distribution", {}))
        self._write(paths["confidence"], analytics.get("confidence_distribution", {}))
        self._write(
            paths["validation"],
            analytics.get("latest", {}).get("validation", {}),
        )
        self._write(paths["coverage"], analytics.get("coverage_distribution", {}))
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
