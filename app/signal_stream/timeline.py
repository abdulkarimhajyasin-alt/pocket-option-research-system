"""Signal stream timeline engine."""

from __future__ import annotations

from collections import Counter

from app.signal_stream.models import SignalEvent
from app.signal_stream.models import SignalTimelineResult
from app.signal_stream.scoring import average
from app.signal_stream.scoring import clamp


class SignalTimelineEngine:
    """Track signal sequence, frequency, density, and activity."""

    def build(self, events: tuple[SignalEvent, ...]) -> SignalTimelineResult:
        rows = tuple(
            {
                "sequence": index,
                "signal_id": event.signal_id,
                "timestamp": event.timestamp,
                "asset": event.asset,
                "session": event.session,
                "direction": event.direction.value,
                "confidence": event.confidence,
            }
            for index, event in enumerate(events, start=1)
        )
        sessions = Counter(event.session for event in events)
        activity = {str(key): float(value) for key, value in sessions.items()}
        frequency = round(len(events) / max(len(sessions), 1), 2)
        density = clamp(min(100.0, len(events) * 5.0))
        score = average([density, average([event.confidence for event in events])])
        return SignalTimelineResult(
            score=score,
            sequence_count=len(events),
            frequency=frequency,
            density=density,
            activity=activity,
            timeline=rows,
        )
