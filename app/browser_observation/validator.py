"""Validation for read-only browser observation artifacts."""

from __future__ import annotations

from app.browser_observation.models import ObservationArtifact
from app.browser_observation.models import SUPPORTED_ARTIFACT_TYPES
from app.browser_observation.models import ValidationResult


def clamp(value: float) -> float:
    """Clamp score values to 0-100."""
    return round(max(0.0, min(100.0, value)), 2)


def average(values: list[float]) -> float:
    """Average bounded score values."""
    if not values:
        return 0.0
    return round(sum(clamp(value) for value in values) / len(values), 2)


class ArtifactValidationEngine:
    """Validate artifact structure, completeness, integrity, and consistency."""

    def validate(
        self,
        artifacts: tuple[ObservationArtifact, ...],
    ) -> ValidationResult:
        count = len(artifacts)
        supported = sum(
            1 for item in artifacts if item.artifact_type in SUPPORTED_ARTIFACT_TYPES
        )
        valid = sum(1 for item in artifacts if item.validation_status == "ناجح")
        visible = sum(1 for item in artifacts if item.visibility_status == "مرئي")
        monitored = sum(1 for item in artifacts if item.monitoring_status == "مستقر")
        structure = (supported / count * 100.0) if count else 0.0
        completeness = (visible / count * 100.0) if count else 0.0
        integrity = (valid / count * 100.0) if count else 0.0
        consistency = (monitored / count * 100.0) if count else 0.0
        return ValidationResult(
            score=average([structure, completeness, integrity, consistency]),
            structure=clamp(structure),
            completeness=clamp(completeness),
            integrity=clamp(integrity),
            consistency=clamp(consistency),
        )
