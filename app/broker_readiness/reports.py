"""Reports for passive broker observation readiness."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class BrokerReadinessReportWriter:
    """Write deterministic broker readiness reports."""

    def __init__(self, output_dir: Path | str = "reports/broker_readiness") -> None:
        self.output_dir = Path(output_dir)

    def export(self, analytics: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "summary": self.output_dir / "readiness_summary.json",
            "capability": self.output_dir / "capability_report.json",
            "validation": self.output_dir / "validation_report.json",
            "restriction": self.output_dir / "restriction_report.json",
            "diagnostics": self.output_dir / "diagnostics_report.json",
            "recommendations": self.output_dir / "recommendations_report.json",
        }
        self._write(
            paths["summary"],
            {
                "summary": analytics.get("summary", {}),
                "readiness_distribution": analytics.get("readiness_distribution", {}),
                "readiness_timeline": analytics.get("readiness_timeline", {}),
                "capability_timeline": analytics.get("capability_timeline", {}),
                "safety_timeline": analytics.get("safety_timeline", {}),
                "latest": analytics.get("latest", {}),
            },
        )
        self._write(paths["capability"], analytics.get("capability_distribution", {}))
        self._write(paths["validation"], analytics.get("validation_distribution", {}))
        self._write(paths["restriction"], analytics.get("restriction_distribution", {}))
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
