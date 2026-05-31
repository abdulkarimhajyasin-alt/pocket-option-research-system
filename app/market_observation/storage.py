"""Storage for canonical market observation outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.market_observation.models import MarketObservationResult


class MarketObservationStorage:
    """Persist the canonical observation source for downstream research."""

    def __init__(self, output_dir: Path | str = "storage/market_observation") -> None:
        self.output_dir = Path(output_dir)

    def save(
        self,
        result: MarketObservationResult,
        analytics: dict[str, Any],
    ) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "canonical": self.output_dir / "canonical_market_observation.json",
            "registry": self.output_dir / "observation_registry.json",
            "validation": self.output_dir / "validation_results.json",
            "metrics": self.output_dir / "observation_metrics.json",
            "diagnostics": self.output_dir / "diagnostics.json",
        }
        self._write(paths["canonical"], result.to_dict())
        self._write(paths["registry"], [item.to_dict() for item in result.observations])
        self._write(paths["validation"], result.validation.to_dict())
        self._write(paths["metrics"], analytics)
        self._write(paths["diagnostics"], [item.to_dict() for item in result.diagnostics])
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
