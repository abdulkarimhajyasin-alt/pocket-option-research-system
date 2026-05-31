"""Monitoring for read-only browser observation artifacts."""

from __future__ import annotations

from app.browser_observation.models import MonitoringResult
from app.browser_observation.models import ObservationArtifact
from app.browser_observation.models import ValidationResult
from app.browser_observation.models import VisibilityResult
from app.browser_observation.validator import average
from app.browser_observation.validator import clamp


class ArtifactMonitoringEngine:
    """Track artifact quality, stability, consistency, and freshness."""

    def monitor(
        self,
        artifacts: tuple[ObservationArtifact, ...],
        validation: ValidationResult,
        visibility: VisibilityResult,
    ) -> MonitoringResult:
        count = len(artifacts)
        stable = sum(1 for item in artifacts if item.monitoring_status == "مستقر")
        readable = sum(1 for item in artifacts if item.metadata.get("readable"))
        freshness = sum(1 for item in artifacts if item.created_at != "0")
        quality = average([validation.score, visibility.score])
        stability = (stable / count * 100.0) if count else 0.0
        consistency = (readable / count * 100.0) if count else 0.0
        freshness_score = (freshness / count * 100.0) if count else 0.0
        return MonitoringResult(
            score=average([quality, stability, consistency, freshness_score]),
            quality=clamp(quality),
            stability=clamp(stability),
            consistency=clamp(consistency),
            freshness=clamp(freshness_score),
        )
