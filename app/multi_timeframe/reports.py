"""Report generation for multi-timeframe confirmation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class MultiTimeframeReportWriter:
    """Write deterministic multi-timeframe reports."""

    def __init__(self, output_dir: Path | str = "reports/multi_timeframe") -> None:
        self.output_dir = Path(output_dir)

    def export(self, analytics: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "alignment": self.output_dir / "alignment_summary.json",
            "confirmation": self.output_dir / "confirmation_summary.json",
            "conflicts": self.output_dir / "conflict_analysis.json",
            "assets": self.output_dir / "asset_alignment.json",
            "sessions": self.output_dir / "session_alignment.json",
            "timeframes": self.output_dir / "timeframe_contribution.json",
            "results": self.output_dir / "confirmation_results.json",
        }
        self._write(
            paths["alignment"],
            {
                "summary": analytics.get("summary", {}),
                "distribution": analytics.get("alignment_distribution", {}),
                "timeline": analytics.get("timeline", {}),
                "latest": analytics.get("latest", []),
                "best_confirmation": analytics.get("best_confirmation", {}),
            },
        )
        self._write(
            paths["confirmation"],
            {
                "distribution": analytics.get("confirmation_distribution", {}),
                "best_confirmation": analytics.get("best_confirmation", {}),
            },
        )
        self._write(paths["conflicts"], analytics.get("conflict_distribution", {}))
        self._write(paths["assets"], analytics.get("asset_alignment", {}))
        self._write(paths["sessions"], analytics.get("session_alignment", {}))
        self._write(paths["timeframes"], analytics.get("timeframe_contribution", {}))
        self._write(paths["results"], analytics.get("latest", []))
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
