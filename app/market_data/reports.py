"""Report generation for market data research integration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class MarketDataReportWriter:
    """Write deterministic dashboard-consumable market data reports."""

    def __init__(self, output_dir: Path | str = "reports/market_data") -> None:
        self.output_dir = Path(output_dir)

    def export(self, analytics: dict[str, Any]) -> dict[str, str]:
        """Export market data reports."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "summary": self.output_dir / "market_summary.json",
            "health": self.output_dir / "market_health.json",
            "latency": self.output_dir / "market_latency.json",
            "assets": self.output_dir / "market_assets.json",
            "sessions": self.output_dir / "market_sessions.json",
            "quality": self.output_dir / "market_quality.json",
        }
        self._write(paths["summary"], analytics.get("summary", {}))
        self._write(paths["health"], analytics.get("health", {}))
        self._write(paths["latency"], analytics.get("latency", []))
        self._write(paths["assets"], analytics.get("assets", []))
        self._write(paths["sessions"], analytics.get("sessions", []))
        self._write(paths["quality"], analytics.get("quality", {}))
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
