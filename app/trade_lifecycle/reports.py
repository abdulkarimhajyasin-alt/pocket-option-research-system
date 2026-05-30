"""Deterministic reports for trade lifecycle research simulation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class TradeLifecycleReportWriter:
    """Write lifecycle report files for dashboard and audit use."""

    def __init__(self, output_dir: Path | str = "reports/trade_lifecycle") -> None:
        self.output_dir = Path(output_dir)

    def export(self, analytics: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "summary": self.output_dir / "lifecycle_summary.json",
            "outcomes": self.output_dir / "outcome_analysis.json",
            "quality": self.output_dir / "quality_analysis.json",
            "success": self.output_dir / "success_analysis.json",
            "failure": self.output_dir / "failure_analysis.json",
            "assets": self.output_dir / "asset_analysis.json",
            "sessions": self.output_dir / "session_analysis.json",
            "confluence": self.output_dir / "confluence_analysis.json",
        }
        self._write(
            paths["summary"],
            {
                "summary": analytics.get("summary", {}),
                "state_distribution": analytics.get("state_distribution", {}),
                "timeline": analytics.get("timeline", {}),
                "latest": analytics.get("latest", []),
                "best_lifecycle": analytics.get("best_lifecycle", {}),
            },
        )
        self._write(paths["outcomes"], analytics.get("outcome_distribution", {}))
        self._write(paths["quality"], analytics.get("quality_distribution", {}))
        self._write(paths["success"], analytics.get("success_factors", {}))
        self._write(paths["failure"], analytics.get("failure_factors", {}))
        self._write(paths["assets"], analytics.get("asset_performance", {}))
        self._write(paths["sessions"], analytics.get("session_performance", {}))
        self._write(paths["confluence"], analytics.get("confluence_performance", {}))
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
