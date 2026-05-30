"""Storage for strategy benchmark outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.strategy_benchmark.models import StrategyBenchmarkResult


class StrategyBenchmarkStorage:
    """Persist benchmark outputs and safely load missing files."""

    def __init__(self, output_dir: Path | str = "storage/strategy_benchmark") -> None:
        self.output_dir = Path(output_dir)

    def save(
        self,
        result: StrategyBenchmarkResult,
        analytics: dict[str, Any],
    ) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "results": self.output_dir / "benchmark_results.json",
            "rankings": self.output_dir / "profile_rankings.json",
            "metrics": self.output_dir / "benchmark_metrics.json",
            "improvements": self.output_dir / "improvement_reports.json",
            "recommendations": self.output_dir / "recommendations.json",
        }
        self._write(paths["results"], result.to_dict())
        self._write(paths["rankings"], [item.to_dict() for item in result.rankings])
        self._write(paths["metrics"], analytics)
        self._write(
            paths["improvements"],
            [item.to_dict() for item in result.improvements],
        )
        self._write(
            paths["recommendations"],
            [item.to_dict() for item in result.recommendations],
        )
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
