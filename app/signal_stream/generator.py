"""Research-only signal event generation."""

from __future__ import annotations

from typing import Any

from app.signal_stream.models import SignalDirection
from app.signal_stream.models import SignalEvent
from app.signal_stream.scoring import clamp


class SignalEventGenerator:
    """Transform passive replay observations into research signal events."""

    def generate(
        self,
        replay_events: list[dict[str, Any]],
        signal_bias: dict[str, float] | None = None,
    ) -> tuple[SignalEvent, ...]:
        bias = signal_bias or {}
        events = []
        for index, row in enumerate(replay_events, start=1):
            observation = row.get("observation", {}) if isinstance(row, dict) else {}
            if not isinstance(observation, dict):
                observation = {}
            confidence = clamp(float(observation.get("confidence") or 0.0))
            quality = clamp(float(observation.get("quality") or 0.0))
            readiness = clamp(float(observation.get("readiness") or 0.0))
            direction = self._direction(index, confidence, quality, readiness, bias)
            events.append(
                SignalEvent(
                    signal_id=f"signal_stream_{index:04d}",
                    timestamp=str(observation.get("timestamp") or ""),
                    asset=str(observation.get("asset") or "research_asset"),
                    session=str(observation.get("session") or "passive"),
                    direction=direction,
                    confidence=confidence,
                    quality=quality,
                    source=str(observation.get("source") or "live_observation"),
                    observation_id=str(observation.get("observation_id") or index),
                    metadata={
                        "research_only": True,
                        "signal_generation_only": True,
                        "not_execution": True,
                        "source_sequence": row.get("sequence"),
                    },
                )
            )
        return tuple(events)

    def _direction(
        self,
        index: int,
        confidence: float,
        quality: float,
        readiness: float,
        bias: dict[str, float],
    ) -> SignalDirection:
        if min(confidence, quality, readiness) < 45:
            return SignalDirection.NO_TRADE
        call_bias = bias.get("CALL", 0.0)
        put_bias = bias.get("PUT", 0.0)
        if call_bias > put_bias and index % 3 != 0:
            return SignalDirection.CALL
        if put_bias > call_bias and index % 3 != 0:
            return SignalDirection.PUT
        return SignalDirection.CALL if index % 2 else SignalDirection.PUT
