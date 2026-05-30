"""Local storage for signal intelligence research artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.signal_intelligence.models import SignalIntelligenceResult


class SignalStorage:
    """Persist signal intelligence state under storage/signals."""

    def __init__(self, output_dir: Path | str = "storage/signals") -> None:
        self.output_dir = Path(output_dir)

    def save(
        self,
        signals: list[SignalIntelligenceResult],
        analytics: dict[str, Any],
    ) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "latest": self.output_dir / "latest_signals.json",
            "history": self.output_dir / "signal_history.json",
            "statistics": self.output_dir / "signal_statistics.json",
            "confidence": self.output_dir / "confidence_distribution.json",
        }
        self._write(paths["latest"], [signal.to_dict() for signal in signals[-10:]])
        self._write(paths["history"], [signal.to_dict() for signal in signals])
        self._write(paths["statistics"], analytics.get("summary", {}))
        self._write(paths["confidence"], analytics.get("confidence_distribution", {}))
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
