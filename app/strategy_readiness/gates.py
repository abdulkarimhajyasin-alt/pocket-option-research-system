"""Deployment gate framework for research readiness."""

from __future__ import annotations

from app.strategy_readiness.models import DeploymentGate


class DeploymentGateEngine:
    """Evaluate research-only gate categories."""

    def evaluate(
        self,
        components: dict[str, float],
        stability_score: float,
    ) -> tuple[DeploymentGate, ...]:
        gates = (
            self._gate("بوابة الإشارة", components.get("جودة الإشارة", 0.0)),
            self._gate("بوابة الأداء", components.get("دقة الثقة", 0.0)),
            self._gate("بوابة الفرصة", components.get("جودة الفرصة", 0.0)),
            self._gate("بوابة الأطر الزمنية", components.get("جودة الأطر الزمنية", 0.0)),
            self._gate("بوابة التوافق", components.get("جودة التوافق", 0.0)),
            self._gate("بوابة دورة الحياة", components.get("جودة دورة الحياة", 0.0)),
            self._gate("بوابة الاستقرار", stability_score),
        )
        return gates

    def _gate(self, name: str, score: float) -> DeploymentGate:
        if score >= 70:
            status = "PASS"
            status_ar = "ناجحة"
            explanation = "البوابة مستوفاة بحثيا."
        elif score >= 45:
            status = "WARNING"
            status_ar = "تحذير"
            explanation = "البوابة تحتاج متابعة بحثية."
        else:
            status = "FAIL"
            status_ar = "فشل"
            explanation = "البوابة غير مستوفاة بحثيا."
        return DeploymentGate(
            name=name,
            status=status,
            status_ar=status_ar,
            score=round(score, 2),
            explanation=explanation,
        )
