"""Signal stream engine."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.signal_stream.generator import SignalEventGenerator
from app.signal_stream.models import SignalStreamResult
from app.signal_stream.scoring import average


class SignalStreamSource:
    """Read local upstream research artifacts for signal stream generation."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)

    def replay_events(self) -> list[dict[str, Any]]:
        payload = self._read_json("reports/live_observation/replay_summary.json")
        latest = payload.get("latest", {}) if isinstance(payload, dict) else {}
        replay = latest.get("replay", {}) if isinstance(latest, dict) else {}
        events = replay.get("events", []) if isinstance(replay, dict) else []
        return [item for item in events if isinstance(item, dict)]

    def signal_bias(self) -> dict[str, float]:
        payload = self._read_json("reports/signals/signal_distribution.json")
        if not payload:
            return {}
        return {str(key): float(value or 0.0) for key, value in payload.items()}

    def _read_json(self, relative: str) -> dict[str, Any]:
        path = self.project_root / relative
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return payload if isinstance(payload, dict) else {}


class SignalStreamEngine:
    """Generate continuous research-only signal events from observation replay."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.source = SignalStreamSource(project_root)
        self.generator = SignalEventGenerator()

    def run(self) -> SignalStreamResult:
        events = self.generator.generate(
            self.source.replay_events(),
            signal_bias=self.source.signal_bias(),
        )
        score = average(
            [
                100.0 if events else 0.0,
                average([item.confidence for item in events]),
                average([item.quality for item in events]),
            ]
        )
        return SignalStreamResult(score=score, event_count=len(events), events=events)
