"""Broker observation readiness engine."""

from __future__ import annotations

from app.broker_readiness.capabilities import average
from app.broker_readiness.models import CapabilityAssessment, ReadinessScore
from app.broker_readiness.models import RestrictionReport, ValidationResult


def readiness_state(score: float) -> str:
    """Return Arabic readiness state."""
    if score >= 95:
        return "جاهزة للمراقبة المتقدمة"
    if score >= 85:
        return "جاهزة بشروط"
    if score >= 70:
        return "تحتاج تحسين محدود"
    if score >= 50:
        return "تحتاج تحسين كبير"
    return "غير مؤهلة"


class BrokerObservationReadinessEngine:
    """Evaluate passive external observation readiness."""

    def evaluate(
        self,
        assessment: CapabilityAssessment,
        validation: ValidationResult,
        restrictions: RestrictionReport,
    ) -> ReadinessScore:
        architecture = validation.observation_architecture
        observation = assessment.observation_capability
        data = assessment.data_collection_capability
        monitoring = assessment.monitoring_capability
        safety = validation.observation_isolation
        compliance = 100.0 if restrictions.status == "PASS" else 0.0
        score = average(architecture, observation, data, monitoring, safety, compliance)
        state = readiness_state(score)
        explanation = f"جاهزية مراقبة خارجية سلبية فقط بحالة {state} ودرجة {score}."
        return ReadinessScore(
            score,
            state,
            explanation,
            architecture,
            observation,
            data,
            monitoring,
            safety,
            compliance,
        )
