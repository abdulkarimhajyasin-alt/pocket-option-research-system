"""Validation for signal stream outputs."""

from __future__ import annotations

from app.signal_stream.models import SignalEvent
from app.signal_stream.models import SignalTimelineResult
from app.signal_stream.models import SignalValidationResult
from app.signal_stream.scoring import average


class SignalStreamValidationEngine:
    """Validate signal integrity, timeline integrity, confidence bounds, consistency."""

    def validate(
        self,
        events: tuple[SignalEvent, ...],
        timeline: SignalTimelineResult,
    ) -> SignalValidationResult:
        signal_integrity = (
            100.0
            if all(item.signal_id and item.observation_id for item in events)
            else 40.0
        )
        timeline_integrity = 100.0 if timeline.sequence_count == len(events) else 50.0
        confidence_bounds = 100.0 if all(0 <= item.confidence <= 100 for item in events) else 0.0
        unique = len({item.signal_id for item in events})
        stream_consistency = 100.0 if unique == len(events) else 70.0
        return SignalValidationResult(
            score=average(
                [
                    signal_integrity,
                    timeline_integrity,
                    confidence_bounds,
                    stream_consistency,
                ]
            ),
            signal_integrity=signal_integrity,
            timeline_integrity=timeline_integrity,
            confidence_bounds=confidence_bounds,
            stream_consistency=stream_consistency,
        )
