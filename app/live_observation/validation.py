"""Validation for live observation replay."""

from __future__ import annotations

from app.live_observation.models import ReplayResult
from app.live_observation.models import ReplayValidationResult
from app.live_observation.models import TimelineResult
from app.live_observation.scoring import average
from app.live_observation.scoring import clamp


class ReplayValidationEngine:
    """Validate sequence integrity, timeline integrity, completeness, and consistency."""

    def validate(
        self,
        replay: ReplayResult,
        timeline: TimelineResult,
    ) -> ReplayValidationResult:
        sequences = [event.sequence for event in replay.events]
        sequence_integrity = 100.0 if sequences == list(range(1, len(sequences) + 1)) else 40.0
        timeline_integrity = 100.0 if timeline.sequence_count == replay.event_count else 50.0
        observation_completeness = clamp(min(100.0, replay.event_count * 12.5))
        replay_consistency = (
            100.0
            if replay.event_count
            == len({event.observation.observation_id for event in replay.events})
            else 70.0
        )
        return ReplayValidationResult(
            score=average(
                [
                    sequence_integrity,
                    timeline_integrity,
                    observation_completeness,
                    replay_consistency,
                ]
            ),
            sequence_integrity=sequence_integrity,
            timeline_integrity=timeline_integrity,
            observation_completeness=observation_completeness,
            replay_consistency=replay_consistency,
        )
