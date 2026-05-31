"""Source validation for the external observation sandbox."""

from __future__ import annotations

from app.external_observation.models import ObservationSource
from app.external_observation.models import SourceValidationResult
from app.external_observation.models import SUPPORTED_SOURCE_TYPES


def clamp(value: float) -> float:
    """Clamp score values to 0-100."""
    return round(max(0.0, min(100.0, value)), 2)


def average(values: list[float]) -> float:
    """Average bounded score values."""
    if not values:
        return 0.0
    return round(sum(clamp(value) for value in values) / len(values), 2)


class SourceValidationEngine:
    """Validate source structure, integrity, completeness, consistency, compatibility."""

    def validate(
        self,
        sources: tuple[ObservationSource, ...],
    ) -> SourceValidationResult:
        count = len(sources)
        valid_sources = sum(1 for item in sources if item.validation_status == "ناجح")
        active_sources = sum(1 for item in sources if item.observation_status == "نشط")
        compatible = sum(1 for item in sources if item.source_type in SUPPORTED_SOURCE_TYPES)
        isolated = sum(1 for item in sources if item.isolation_status == "معزول")
        scopes = {item.visibility_scope for item in sources}
        structure = 100.0 if count >= 4 else count * 25.0
        integrity = (valid_sources / count * 100.0) if count else 0.0
        completeness = (active_sources / count * 100.0) if count else 0.0
        consistency = (isolated / count * 100.0) if count else 0.0
        compatibility = (compatible / count * 100.0) if count else 0.0
        if len(scopes) < 3:
            consistency = clamp(consistency - 10.0)
        return SourceValidationResult(
            score=average(
                [structure, integrity, completeness, consistency, compatibility]
            ),
            structure=clamp(structure),
            integrity=clamp(integrity),
            completeness=clamp(completeness),
            consistency=clamp(consistency),
            compatibility=clamp(compatibility),
        )
