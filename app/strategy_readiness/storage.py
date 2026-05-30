"""Storage for strategy readiness outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.strategy_readiness.models import StrategyReadinessResult


class StrategyReadinessStorage:
    """Persist readiness outputs safely."""

    def __init__(self, output_dir: Path | str = "storage/strategy_readiness") -> None:
        self.output_dir = Path(output_dir)

    def save(
        self,
        result: StrategyReadinessResult,
        analytics: dict[str, Any],
    ) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "readiness": self.output_dir / "readiness_results.json",
            "gates": self.output_dir / "gate_results.json",
            "diagnostics": self.output_dir / "diagnostics.json",
            "recommendations": self.output_dir / "recommendations.json",
            "stability": self.output_dir / "stability_metrics.json",
        }
        self._write(paths["readiness"], result.to_dict())
        self._write(paths["gates"], [gate.to_dict() for gate in result.gates])
        self._write(paths["diagnostics"], result.diagnostics.to_dict())
        self._write(
            paths["recommendations"],
            [item.to_dict() for item in result.recommendations],
        )
        self._write(paths["stability"], result.stability.to_dict())
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
