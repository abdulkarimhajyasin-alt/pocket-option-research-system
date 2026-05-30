"""Report generation for opportunity qualification."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class OpportunityReportWriter:
    """Write deterministic opportunity qualification reports."""

    def __init__(self, output_dir: Path | str = "reports/opportunities") -> None:
        self.output_dir = Path(output_dir)

    def export(self, analytics: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "summary": self.output_dir / "opportunity_summary.json",
            "rankings": self.output_dir / "opportunity_rankings.json",
            "qualification": self.output_dir / "qualification_analysis.json",
            "assets": self.output_dir / "asset_rankings.json",
            "sessions": self.output_dir / "session_rankings.json",
            "structures": self.output_dir / "structure_rankings.json",
            "rejections": self.output_dir / "rejection_analysis.json",
        }
        self._write(paths["summary"], analytics.get("summary", {}))
        self._write(paths["rankings"], analytics.get("rankings", []))
        self._write(paths["qualification"], analytics.get("qualification_distribution", {}))
        self._write(paths["assets"], analytics.get("asset_ranking", {}))
        self._write(paths["sessions"], analytics.get("session_ranking", {}))
        self._write(paths["structures"], analytics.get("structure_ranking", {}))
        self._write(paths["rejections"], analytics.get("rejection_distribution", {}))
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
