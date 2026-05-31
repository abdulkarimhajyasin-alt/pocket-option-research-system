"""External observation sandbox engine."""

from __future__ import annotations

from app.external_observation.models import HealthResult
from app.external_observation.models import IsolationStatus
from app.external_observation.models import MonitoringResult
from app.external_observation.models import ObservationSource
from app.external_observation.models import SandboxScore
from app.external_observation.models import SourceValidationResult
from app.external_observation.validation import average


def sandbox_state(score: float) -> tuple[str, str]:
    """Return Arabic state and explanation for a sandbox score."""
    if score >= 95:
        return "جاهز للمراقبة المتقدمة", "الصندوق مؤهل لمصادر مراقبة متقدمة."
    if score >= 85:
        return "جاهز بشروط", "الصندوق صالح مع متابعة بعض التحسينات."
    if score >= 70:
        return "يحتاج تحسين محدود", "الصندوق صالح بحثيا مع فجوات محدودة."
    if score >= 50:
        return "يحتاج تحسين كبير", "الصندوق يحتاج تحسينات قبل التوسع."
    return "غير مؤهل", "الصندوق غير مؤهل لمصادر مراقبة إضافية."


class ObservationHealthEngine:
    """Evaluate validation, monitoring, isolation, and reporting health."""

    def evaluate(
        self,
        validation: SourceValidationResult,
        monitoring: MonitoringResult,
        isolation: IsolationStatus,
        sources: tuple[ObservationSource, ...],
    ) -> HealthResult:
        reporting_health = 100.0 if sources else 0.0
        score = average(
            [
                validation.score,
                monitoring.score,
                isolation.score,
                reporting_health,
            ]
        )
        state, explanation = sandbox_state(score)
        return HealthResult(
            score=score,
            state=state,
            explanation=explanation,
            validation_health=validation.score,
            monitoring_health=monitoring.score,
            isolation_health=isolation.score,
            reporting_health=reporting_health,
        )


class ExternalObservationSandbox:
    """Register, validate, isolate, monitor, and score passive sources."""

    def score(
        self,
        validation: SourceValidationResult,
        monitoring: MonitoringResult,
        isolation: IsolationStatus,
        health: HealthResult,
    ) -> SandboxScore:
        score = average(
            [validation.score, monitoring.score, isolation.score, health.score]
        )
        state, explanation = sandbox_state(score)
        return SandboxScore(score=score, state=state, explanation=explanation)
