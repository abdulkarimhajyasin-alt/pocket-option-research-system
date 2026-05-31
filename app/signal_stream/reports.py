"""Reports for signal stream engine."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class SignalStreamReportWriter:
    """Write dashboard reports for signal stream."""

    def __init__(self, output_dir: Path | str = "reports/signal_stream") -> None:
        self.output_dir = Path(output_dir)

    def export(self, analytics: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "summary": self.output_dir / "signal_summary.json",
            "stream": self.output_dir / "stream_report.json",
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
                "latest": analytics.get("latest", {}),
            },
        )
        self._write(paths["stream"], analytics.get("signal_distribution", {}))
        self._write(paths["quality"], analytics.get("quality_distribution", {}))
        self._write(paths["readiness"], analytics.get("readiness_distribution", {}))
        self._write(
            paths["validation"],
            analytics.get("latest", {}).get("validation", {}),
        )
        self._write(paths["diagnostics"], analytics.get("diagnostics_distribution", {}))
        self._write(paths["recommendations"], analytics.get("recommendation_distribution", {}))
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
