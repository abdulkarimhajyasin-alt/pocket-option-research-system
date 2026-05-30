"""Storage for signal performance research artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.signal_performance.models import PaperTradeResult, SignalOutcome, TrackedSignal


class SignalPerformanceStorage:
    """Persist signal performance files under storage/signal_performance."""

    def __init__(self, output_dir: Path | str = "storage/signal_performance") -> None:
        self.output_dir = Path(output_dir)

    def save(
        self,
        tracked: list[TrackedSignal],
        results: list[PaperTradeResult],
        outcomes: list[SignalOutcome],
        analytics: dict[str, Any],
    ) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "tracked": self.output_dir / "tracked_signals.json",
            "results": self.output_dir / "paper_trade_results.json",
            "metrics": self.output_dir / "performance_metrics.json",
            "confidence": self.output_dir / "confidence_validation.json",
            "outcomes": self.output_dir / "signal_outcomes.json",
        }
        self._write(paths["tracked"], [item.to_dict() for item in tracked])
        self._write(paths["results"], [item.to_dict() for item in results])
        self._write(paths["metrics"], analytics.get("summary", {}))
        self._write(paths["confidence"], analytics.get("confidence_validation", {}))
        self._write(paths["outcomes"], [item.to_dict() for item in outcomes])
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
