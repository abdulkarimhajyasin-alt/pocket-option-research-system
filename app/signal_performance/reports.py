"""Reports for signal performance validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class SignalPerformanceReportWriter:
    """Write deterministic signal performance reports."""

    def __init__(self, output_dir: Path | str = "reports/signal_performance") -> None:
        self.output_dir = Path(output_dir)

    def export(self, analytics: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "summary": self.output_dir / "performance_summary.json",
            "win_rate": self.output_dir / "win_rate_analysis.json",
            "assets": self.output_dir / "asset_performance.json",
            "sessions": self.output_dir / "session_performance.json",
            "confidence": self.output_dir / "confidence_validation.json",
            "structure": self.output_dir / "structure_performance.json",
            "quality": self.output_dir / "signal_quality.json",
            "stability": self.output_dir / "stability_analysis.json",
        }
        self._write(paths["summary"], analytics.get("summary", {}))
        self._write(paths["win_rate"], analytics.get("outcomes", {}))
        self._write(paths["assets"], analytics.get("asset_performance", {}))
        self._write(paths["sessions"], analytics.get("session_performance", {}))
        self._write(paths["confidence"], analytics.get("confidence_validation", {}))
        self._write(paths["structure"], analytics.get("structure_performance", {}))
        self._write(paths["quality"], self._quality_payload(analytics))
        self._write(paths["stability"], analytics.get("timeline", {}))
        return {key: str(path) for key, path in paths.items()}

    def _quality_payload(self, analytics: dict[str, Any]) -> dict[str, Any]:
        summary = analytics.get("summary", {})
        return {
            "signal_quality_score": summary.get("signal_quality_score", 0.0),
            "consistency_score": summary.get("consistency_score", 0.0),
            "stability_score": summary.get("stability_score", 0.0),
            "confidence_accuracy_score": summary.get("confidence_accuracy_score", 0.0),
            "validation_readiness_score": summary.get("validation_readiness_score", 0.0),
        }

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
