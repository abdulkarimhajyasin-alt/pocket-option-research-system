"""Research risk monitoring."""

from __future__ import annotations

from app.research_ops.models import RiskAssessment, StrategyStatus


class RiskMonitor:
    """Track research risks without trading implications."""

    def evaluate(self, strategy: StrategyStatus, opportunity_count: int) -> RiskAssessment:
        risks: list[str] = []
        if strategy.confidence_stability < 60:
            risks.append("ضعف الثقة")
        if strategy.readiness_score < 70:
            risks.append("عدم استقرار الجاهزية")
        if strategy.lifecycle_quality < 60:
            risks.append("ضعف جودة دورة الحياة")
        if strategy.research_quality < 60:
            risks.append("ضعف جودة الفرص")
        if strategy.failures > 0:
            risks.append("فشل بعض البوابات")
        if opportunity_count < 50:
            risks.append("نقص البيانات")
        score = max(0.0, 100.0 - len(risks) * 15.0)
        return RiskAssessment(
            severity=self._severity(len(risks)),
            risks=risks,
            score=round(score, 2),
        )

    def _severity(self, count: int) -> str:
        if count >= 4:
            return "مرتفع"
        if count >= 2:
            return "متوسط"
        return "منخفض"
