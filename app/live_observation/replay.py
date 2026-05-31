"""Observation replay engine."""

from __future__ import annotations

from app.live_observation.models import LiveObservation
from app.live_observation.models import ReplayEvent
from app.live_observation.models import ReplayResult
from app.live_observation.scheduler import ObservationReplayScheduler
from app.live_observation.scoring import average
from app.live_observation.scoring import clamp


class ObservationReplayEngine:
    """Replay historical and imported observations as simulated live events."""

    def __init__(self) -> None:
        self.scheduler = ObservationReplayScheduler()
        self._state = "جاهز"

    def pause(self) -> str:
        self._state = "متوقف"
        return self._state

    def resume(self) -> str:
        self._state = "يعمل"
        return self._state

    def reset(self) -> str:
        self._state = "جاهز"
        return self._state

    def replay(
        self,
        observations: tuple[LiveObservation, ...],
        speed_multiplier: int = 10,
    ) -> ReplayResult:
        schedule = self.scheduler.build(len(observations), speed_multiplier)
        events = tuple(
            ReplayEvent(
                sequence=index + 1,
                observation=observation,
                simulated_offset_seconds=schedule.offsets[index],
                speed_multiplier=speed_multiplier,
                state="مكتمل",
            )
            for index, observation in enumerate(observations)
        )
        score = average(
            [
                100.0 if observations else 0.0,
                average([item.quality for item in observations]),
                average([item.confidence for item in observations]),
                average([item.readiness for item in observations]),
            ]
        )
        self._state = "مكتمل" if observations else "يحتاج مراجعة"
        return ReplayResult(
            score=clamp(score),
            speed_multiplier=speed_multiplier,
            state=self._state,
            event_count=len(events),
            pause_supported=True,
            resume_supported=True,
            reset_supported=True,
            events=events,
        )
