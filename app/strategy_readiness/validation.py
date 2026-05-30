"""Research stability and gate requirement validation."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Any

from app.strategy_readiness.models import GateRequirementReport
from app.strategy_readiness.models import ResearchStabilityScore
from app.strategy_readiness.scoring import bound


@dataclass(frozen=True)
class GateThresholds:
    """Configurable readiness gate thresholds."""

    minimum_signal_count: int = 25
    minimum_validation_count: int = 20
    minimum_confidence_accuracy: float = 60.0
    minimum_consistency_score: float = 45.0
    minimum_readiness_score: float = 50.0


class ResearchStabilityEngine:
    """Evaluate repeatability, consistency, and reliability."""

    def evaluate(self, inputs: dict[str, Any]) -> ResearchStabilityScore:
        performance = inputs.get("performance_summary", {})
        signal = inputs.get("signal_summary", {})
        lifecycle = inputs.get("lifecycle_summary", {})
        consistency = self._float(performance.get("consistency_score"))
        confidence = self._float(performance.get("confidence_accuracy_score"))
        signal_count = self._float(signal.get("total_signals"))
        lifecycle_count = self._float(lifecycle.get("total_lifecycles"))
        repeatability = bound(min(100.0, lifecycle_count / 2))
        signal_reliability = bound(min(100.0, signal_count / 2))
        values = [consistency, confidence, repeatability, signal_reliability]
        average = mean(values) if values else 0.0
        variance = mean([(value - average) ** 2 for value in values]) if values else 0.0
        stability = bound(average - min(30.0, variance / 100))
        return ResearchStabilityScore(
            score=stability,
            consistency=bound(consistency),
            variance=round(variance, 2),
            repeatability=repeatability,
            confidence_reliability=bound(confidence),
            signal_reliability=signal_reliability,
        )

    def _float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0


class GateRequirementsEngine:
    """Check configurable minimum research requirements."""

    def __init__(self, thresholds: GateThresholds | None = None) -> None:
        self.thresholds = thresholds or GateThresholds()

    def evaluate(
        self,
        inputs: dict[str, Any],
        readiness_score: float,
    ) -> GateRequirementReport:
        signal_count = self._float(inputs.get("signal_summary", {}).get("total_signals"))
        validation_count = self._float(
            inputs.get("performance_summary", {}).get("total_signals")
        )
        confidence = self._float(
            inputs.get("performance_summary", {}).get("confidence_accuracy_score")
        )
        consistency = self._float(
            inputs.get("performance_summary", {}).get("consistency_score")
        )
        warnings = []
        if signal_count < self.thresholds.minimum_signal_count:
            warnings.append("حجم الإشارات أقل من الحد الأدنى")
        if validation_count < self.thresholds.minimum_validation_count:
            warnings.append("حجم التحقق أقل من الحد الأدنى")
        if confidence < self.thresholds.minimum_confidence_accuracy:
            warnings.append("دقة الثقة أقل من الحد الأدنى")
        if consistency < self.thresholds.minimum_consistency_score:
            warnings.append("اتساق البحث أقل من الحد الأدنى")
        if readiness_score < self.thresholds.minimum_readiness_score:
            warnings.append("درجة الجاهزية أقل من الحد الأدنى")
        return GateRequirementReport(
            minimum_signal_count=self.thresholds.minimum_signal_count,
            minimum_validation_count=self.thresholds.minimum_validation_count,
            minimum_confidence_accuracy=self.thresholds.minimum_confidence_accuracy,
            minimum_consistency_score=self.thresholds.minimum_consistency_score,
            minimum_readiness_score=self.thresholds.minimum_readiness_score,
            passed=not warnings,
            warnings=warnings,
        )

    def _float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
