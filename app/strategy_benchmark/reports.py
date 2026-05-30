"""Deterministic strategy benchmark reports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class StrategyBenchmarkReportWriter:
    """Write benchmark reports for dashboard and audit use."""

    def __init__(self, output_dir: Path | str = "reports/strategy_benchmark") -> None:
        self.output_dir = Path(output_dir)

    def export(self, analytics: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "summary": self.output_dir / "benchmark_summary.json",
            "rankings": self.output_dir / "profile_rankings.json",
            "improvement": self.output_dir / "improvement_analysis.json",
            "stability": self.output_dir / "stability_analysis.json",
            "robustness": self.output_dir / "robustness_analysis.json",
            "recommendations": self.output_dir / "recommendations_report.json",
        }
        self._write(
            paths["summary"],
            {
                "summary": analytics.get("summary", {}),
                "best_profile": analytics.get("best_profile", {}),
                "benchmark_distribution": analytics.get("benchmark_distribution", {}),
                "readiness_distribution": analytics.get("readiness_distribution", {}),
                "stability_distribution": analytics.get("stability_distribution", {}),
                "quality_distribution": analytics.get("quality_distribution", {}),
                "timeline": analytics.get("timeline", {}),
                "strengths": analytics.get("strengths", {}),
                "weaknesses": analytics.get("weaknesses", {}),
                "latest": analytics.get("latest", {}),
            },
        )
        self._write(paths["rankings"], analytics.get("ranking_distribution", {}))
        self._write(paths["improvement"], analytics.get("improvements", {}))
        self._write(paths["stability"], analytics.get("stability_distribution", {}))
        self._write(paths["robustness"], analytics.get("robustness_distribution", {}))
        self._write(
            paths["recommendations"],
            analytics.get("latest", {}).get("recommendations", []),
        )
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
