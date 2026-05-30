"""Deterministic research operations alerts."""

from __future__ import annotations

from app.research_ops.models import ResearchAlert, RiskAssessment, StrategyStatus


class ResearchAlertEngine:
    """Generate alerts from research quality and risk state."""

    def generate(
        self,
        strategy: StrategyStatus,
        risk: RiskAssessment,
    ) -> tuple[ResearchAlert, ...]:
        alerts: list[ResearchAlert] = []
        if strategy.confidence_stability < 60:
            alerts.append(self._alert("انخفاض جودة الإشارات", "تحسين الثقة"))
        if strategy.readiness_score < 70:
            alerts.append(self._alert("تراجع الاستقرار", "زيادة حجم العينة"))
        if strategy.research_quality < 65:
            alerts.append(self._alert("ضعف التوافق", "تحسين التوافق العام"))
        if strategy.lifecycle_quality < 60:
            alerts.append(self._alert("ضعف جودة الفرص", "مراجعة دورة حياة الفرص"))
        if "نقص البيانات" in risk.risks:
            alerts.append(self._alert("نقص البيانات", "زيادة حجم العينة"))
        return tuple(alerts)

    def _alert(self, title: str, recommendation: str) -> ResearchAlert:
        return ResearchAlert(
            title=title,
            severity="متوسط",
            explanation="تنبيه بحثي حتمي بناء على مؤشرات الجودة الحالية.",
            recommendation=recommendation,
        )
