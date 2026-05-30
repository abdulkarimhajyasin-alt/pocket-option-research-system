"""Storage for market regime outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.market_regime.models import MarketRegimeRun


class MarketRegimeStorage:
    """Persist market regime outputs and handle missing files safely."""

    def __init__(self, output_dir: Path | str = "storage/market_regime") -> None:
        self.output_dir = Path(output_dir)

    def save(self, result: MarketRegimeRun, analytics: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "regime": self.output_dir / "market_regime.json",
            "volatility": self.output_dir / "volatility_metrics.json",
            "trend": self.output_dir / "trend_metrics.json",
            "transition": self.output_dir / "transition_metrics.json",
            "compatibility": self.output_dir / "compatibility_metrics.json",
            "statistics": self.output_dir / "regime_statistics.json",
        }
        self._write(paths["regime"], result.to_dict())
        self._write(paths["volatility"], result.regime.volatility.to_dict())
        self._write(paths["trend"], result.regime.trend.to_dict())
        self._write(paths["transition"], result.regime.transition.to_dict())
        self._write(paths["compatibility"], result.compatibility.to_dict())
        self._write(paths["statistics"], analytics)
        return {key: str(path) for key, path in paths.items()}

    def load_json(self, name: str, default: Any) -> Any:
        path = self.output_dir / name
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
