"""Capability assessment for passive broker observation readiness."""

from __future__ import annotations

from app.broker_readiness.models import CapabilityAssessment, ObservationCapability


def clamp(value: float) -> float:
    """Clamp a score to 0-100."""
    return round(max(0.0, min(100.0, float(value))), 2)


def average(*values: float) -> float:
    """Average scores."""
    return round(sum(clamp(value) for value in values) / len(values), 2) if values else 0.0


class CapabilityAssessmentEngine:
    """Assess passive observation capability."""

    def assess(self, capability: ObservationCapability) -> CapabilityAssessment:
        data_collection = average(
            capability.market_visibility,
            capability.asset_visibility,
            capability.candle_visibility,
        )
        observation = capability.score
        reporting = average(capability.session_visibility, capability.signal_visibility)
        monitoring = average(capability.market_visibility, capability.session_visibility)
        diagnostics = average(capability.payout_visibility, capability.asset_visibility)
        score = average(data_collection, observation, reporting, monitoring, diagnostics)
        return CapabilityAssessment(
            score,
            data_collection,
            observation,
            reporting,
            monitoring,
            diagnostics,
        )
