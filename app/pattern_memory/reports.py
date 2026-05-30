"""Deterministic reports for pattern memory."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class PatternMemoryReportWriter:
    """Write pattern memory reports for dashboard and audit use."""

    def __init__(self, output_dir: Path | str = "reports/pattern_memory") -> None:
        self.output_dir = Path(output_dir)

    def export(self, analytics: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "summary": self.output_dir / "pattern_summary.json",
            "rankings": self.output_dir / "pattern_rankings.json",
            "quality": self.output_dir / "pattern_quality.json",
            "similarity": self.output_dir / "similarity_analysis.json",
            "learning": self.output_dir / "learning_analysis.json",
            "adaptation": self.output_dir / "adaptation_analysis.json",
            "stability": self.output_dir / "stability_analysis.json",
            "reliability": self.output_dir / "reliability_analysis.json",
        }
        self._write(
            paths["summary"],
            {
                "summary": analytics.get("summary", {}),
                "best_pattern": analytics.get("best_pattern", {}),
                "pattern_rankings": analytics.get("pattern_rankings", {}),
                "session_rankings": analytics.get("session_rankings", {}),
                "asset_rankings": analytics.get("asset_rankings", {}),
                "structure_rankings": analytics.get("structure_rankings", {}),
                "fvg_rankings": analytics.get("fvg_rankings", {}),
                "cisd_rankings": analytics.get("cisd_rankings", {}),
                "reliability_timeline": analytics.get("reliability_timeline", {}),
                "latest": analytics.get("latest", {}),
            },
        )
        self._write(paths["rankings"], analytics.get("pattern_rankings", {}))
        self._write(paths["quality"], analytics.get("pattern_quality", {}))
        self._write(paths["similarity"], analytics.get("similarity_distribution", {}))
        self._write(paths["learning"], analytics.get("learning_progress", {}))
        self._write(paths["adaptation"], analytics.get("adaptation_analysis", {}))
        self._write(paths["stability"], analytics.get("stability_distribution", {}))
        self._write(paths["reliability"], analytics.get("reliability_timeline", {}))
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
