"""Reports for live observation replay."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class LiveObservationReportWriter:
    """Write deterministic dashboard reports for live observation replay."""

    def __init__(self, output_dir: Path | str = "reports/live_observation") -> None:
        self.output_dir = Path(output_dir)

    def export(self, analytics: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "summary": self.output_dir / "replay_summary.json",
            "timeline": self.output_dir / "timeline_report.json",
            "quality": self.output_dir / "quality_report.json",
            "readiness": self.output_dir / "readiness_report.json",
            "validation": self.output_dir / "validation_report.json",
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
        self._write(paths["timeline"], analytics.get("timeline_activity", {}))
        self._write(paths["quality"], analytics.get("replay_quality", {}))
        self._write(paths["readiness"], analytics.get("replay_readiness", {}))
        self._write(paths["validation"], analytics.get("replay_validation", {}))
        self._write(paths["diagnostics"], analytics.get("diagnostics_distribution", {}))
        self._write(paths["recommendations"], analytics.get("recommendation_distribution", {}))
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
