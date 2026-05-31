"""Passive observation capability builder."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.broker_readiness.models import ObservationCapability
from app.broker_readiness.capabilities import clamp


class ObservationCapabilityBuilder:
    """Build passive capability scores from existing local observation reports."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)

    def build(self) -> ObservationCapability:
        observation = self._load("reports/observation/observation_summary.json")
        market = self._load("reports/market_data/market_summary.json")
        signals = self._load("reports/signals/signal_summary.json")
        return ObservationCapability(
            market_visibility=self._score(market, "feed_quality_score", 70),
            asset_visibility=self._score(observation, "active_assets", 65, scale=12),
            payout_visibility=self._score(observation, "average_payout", 60),
            session_visibility=self._score(observation, "active_sessions", 60, scale=25),
            candle_visibility=self._score(market, "readiness_score", 70),
            signal_visibility=self._score(signals, "total_signals", 65, scale=0.75),
        )

    def _load(self, relative_path: str) -> dict[str, Any]:
        path = self.project_root / relative_path
        if not path.exists():
            return {}
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict) and isinstance(payload.get("summary"), dict):
            return payload["summary"]
        return payload if isinstance(payload, dict) else {}

    def _score(
        self,
        payload: dict[str, Any],
        key: str,
        default: float,
        *,
        scale: float = 1.0,
    ) -> float:
        value = payload.get(key)
        if value is None:
            return default
        try:
            return clamp(float(value) * scale)
        except (TypeError, ValueError):
            return default
