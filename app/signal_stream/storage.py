"""Storage for signal stream outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.signal_stream.models import SignalStreamRun


class SignalStreamStorage:
    """Persist signal stream research outputs."""

    def __init__(self, output_dir: Path | str = "storage/signal_stream") -> None:
        self.output_dir = Path(output_dir)

    def save(self, result: SignalStreamRun, analytics: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "events": self.output_dir / "signal_events.json",
            "queue": self.output_dir / "signal_queue.json",
            "timeline": self.output_dir / "timeline_results.json",
            "quality": self.output_dir / "quality_results.json",
            "readiness": self.output_dir / "readiness_results.json",
            "validation": self.output_dir / "validation_results.json",
            "diagnostics": self.output_dir / "diagnostics.json",
        }
        self._write(paths["events"], [item.to_dict() for item in result.stream.events])
        self._write(paths["queue"], result.queue.to_dict())
        self._write(paths["timeline"], result.timeline.to_dict())
        self._write(paths["quality"], result.scoring.to_dict())
        self._write(paths["readiness"], analytics.get("summary", {}))
        self._write(paths["validation"], result.validation.to_dict())
        self._write(paths["diagnostics"], analytics)
        return {key: str(path) for key, path in paths.items()}

    def _write(self, path: Path, payload: Any) -> None:
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
