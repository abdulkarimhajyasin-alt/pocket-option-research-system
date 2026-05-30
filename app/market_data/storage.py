"""Local storage for market data research snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.market_data.models import MarketSnapshot


class MarketDataStorage:
    """Persist safe local market-data research files."""

    def __init__(self, output_dir: Path | str = "storage/market_data") -> None:
        self.output_dir = Path(output_dir)

    def save(self, snapshot: MarketSnapshot, analytics: dict[str, Any]) -> dict[str, str]:
        """Persist latest market snapshot and metrics."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "snapshot": self.output_dir / "latest_market_snapshot.json",
            "assets": self.output_dir / "asset_registry.json",
            "health": self.output_dir / "market_health.json",
            "metrics": self.output_dir / "market_metrics.json",
            "sessions": self.output_dir / "session_activity.json",
        }
        self._write(paths["snapshot"], snapshot.to_dict())
        self._write(paths["assets"], [asset.to_dict() for asset in snapshot.assets])
        self._write(paths["health"], analytics.get("health", {}))
        self._write(paths["metrics"], analytics.get("summary", {}))
        self._write(paths["sessions"], analytics.get("quality", {}).get("session_activity", {}))
        return {key: str(path) for key, path in paths.items()}

    def load_json(self, name: str, default: Any) -> Any:
        """Load a storage file safely when it exists."""
        path = self.output_dir / name
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
