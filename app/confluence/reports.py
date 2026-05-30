"""Deterministic reports for confluence research decisions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ConfluenceReportWriter:
    """Write dashboard and audit reports for confluence analytics."""

    def __init__(self, output_dir: Path | str = "reports/confluence") -> None:
        self.output_dir = Path(output_dir)

    def export(self, analytics: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "summary": self.output_dir / "confluence_summary.json",
            "factors": self.output_dir / "factor_analysis.json",
            "assets": self.output_dir / "asset_confluence.json",
            "sessions": self.output_dir / "session_confluence.json",
            "timeframes": self.output_dir / "timeframe_confluence.json",
            "rejections": self.output_dir / "rejection_analysis.json",
            "decisions": self.output_dir / "decision_summary.json",
        }
        self._write(
            paths["summary"],
            {
                "summary": analytics.get("summary", {}),
                "distribution": analytics.get("confluence_distribution", {}),
                "quality": analytics.get("quality_analysis", {}),
                "timeline": analytics.get("timeline", {}),
                "latest": analytics.get("latest", []),
                "best_decision": analytics.get("best_decision", {}),
            },
        )
        self._write(paths["factors"], analytics.get("factor_contribution", {}))
        self._write(paths["assets"], analytics.get("asset_ranking", {}))
        self._write(paths["sessions"], analytics.get("session_ranking", {}))
        self._write(paths["timeframes"], analytics.get("timeframe_ranking", {}))
        self._write(paths["rejections"], analytics.get("rejection_analysis", {}))
        self._write(paths["decisions"], analytics.get("latest", []))
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
