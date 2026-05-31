"""Reports for the external observation sandbox."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ExternalObservationReportWriter:
    """Write deterministic external observation sandbox reports."""

    def __init__(self, output_dir: Path | str = "reports/external_observation") -> None:
        self.output_dir = Path(output_dir)

    def export(self, analytics: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "summary": self.output_dir / "sandbox_summary.json",
            "sources": self.output_dir / "source_report.json",
            "validation": self.output_dir / "validation_report.json",
            "monitoring": self.output_dir / "monitoring_report.json",
            "health": self.output_dir / "health_report.json",
            "diagnostics": self.output_dir / "diagnostics_report.json",
            "recommendations": self.output_dir / "recommendations_report.json",
        }
        self._write(
            paths["summary"],
            {
                "summary": analytics.get("summary", {}),
                "source_distribution": analytics.get("source_distribution", {}),
                "latest": analytics.get("latest", {}),
            },
        )
        self._write(paths["sources"], analytics.get("source_distribution", {}))
        self._write(paths["validation"], analytics.get("validation_distribution", {}))
        self._write(paths["monitoring"], analytics.get("monitoring_distribution", {}))
        self._write(paths["health"], analytics.get("health_distribution", {}))
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
