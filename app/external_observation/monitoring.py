"""Passive monitoring for external observation sources."""

from __future__ import annotations

from app.external_observation.models import MonitoringResult
from app.external_observation.models import ObservationSource
from app.external_observation.validation import average
from app.external_observation.validation import clamp


class ObservationMonitoringEngine:
    """Track source uptime, quality, consistency, coverage, and stability."""

    def monitor(
        self,
        sources: tuple[ObservationSource, ...],
        validation_score: float,
    ) -> MonitoringResult:
        count = len(sources)
        active = sum(1 for item in sources if item.observation_status == "نشط")
        valid = sum(1 for item in sources if item.validation_status == "ناجح")
        isolated = sum(1 for item in sources if item.isolation_status == "معزول")
        uptime = (active / count * 100.0) if count else 0.0
        quality = (valid / count * 100.0) if count else 0.0
        consistency = (isolated / count * 100.0) if count else 0.0
        coverage = min(100.0, count * 25.0)
        stability = average([uptime, quality, consistency, validation_score])
        return MonitoringResult(
            score=average([uptime, quality, consistency, coverage, stability]),
            uptime=clamp(uptime),
            quality=clamp(quality),
            consistency=clamp(consistency),
            coverage=clamp(coverage),
            stability=clamp(stability),
        )
