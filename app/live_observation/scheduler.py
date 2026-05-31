"""Deterministic timing scheduler for observation replay."""

from __future__ import annotations

from dataclasses import dataclass


SUPPORTED_SPEEDS = (1, 2, 5, 10, 25, 50)


@dataclass(frozen=True)
class ReplaySchedule:
    """Replay timing plan with simulated offsets only."""

    speed_multiplier: int
    offsets: tuple[float, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "speed_multiplier": self.speed_multiplier,
            "offsets": list(self.offsets),
            "supported_speeds": list(SUPPORTED_SPEEDS),
        }


class ObservationReplayScheduler:
    """Create deterministic replay offsets without sleeping or connecting."""

    def build(self, count: int, speed_multiplier: int = 10) -> ReplaySchedule:
        if speed_multiplier not in SUPPORTED_SPEEDS:
            raise ValueError("Unsupported replay speed multiplier")
        base_interval = 60.0 / speed_multiplier
        return ReplaySchedule(
            speed_multiplier=speed_multiplier,
            offsets=tuple(round(index * base_interval, 2) for index in range(count)),
        )
