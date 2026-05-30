"""Deterministic market regime reports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class MarketRegimeReportWriter:
    """Write market regime reports for dashboard and audit use."""

    def __init__(self, output_dir: Path | str = "reports/market_regime") -> None:
        self.output_dir = Path(output_dir)

    def export(self, analytics: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "summary": self.output_dir / "regime_summary.json",
            "volatility": self.output_dir / "volatility_analysis.json",
            "trend": self.output_dir / "trend_analysis.json",
            "transition": self.output_dir / "transition_analysis.json",
            "compatibility": self.output_dir / "compatibility_analysis.json",
            "stability": self.output_dir / "stability_analysis.json",
            "quality": self.output_dir / "quality_analysis.json",
        }
        self._write(
            paths["summary"],
            {
                "summary": analytics.get("summary", {}),
                "regime_distribution": analytics.get("regime_distribution", {}),
                "historical_performance": analytics.get("historical_performance", {}),
                "latest": analytics.get("latest", {}),
            },
        )
        self._write(paths["volatility"], analytics.get("volatility_distribution", {}))
        self._write(paths["trend"], analytics.get("trend_distribution", {}))
        self._write(paths["transition"], analytics.get("transition_frequency", {}))
        self._write(paths["compatibility"], analytics.get("compatibility_analysis", {}))
        self._write(paths["stability"], analytics.get("regime_stability", {}))
        self._write(paths["quality"], analytics.get("regime_quality", {}))
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
