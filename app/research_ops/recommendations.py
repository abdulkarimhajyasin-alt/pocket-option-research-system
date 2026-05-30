"""Research operations recommendations and next action."""

from __future__ import annotations

from app.research_ops.models import NextAction, PriorityRecommendation
from app.research_ops.models import ResearchAlert, RiskAssessment


class ResearchRecommendationEngine:
    """Generate prioritized operations recommendations."""

    def generate(
        self,
        alerts: tuple[ResearchAlert, ...],
        risk: RiskAssessment,
    ) -> tuple[PriorityRecommendation, ...]:
        recommendations: list[PriorityRecommendation] = []
        for alert in alerts:
            recommendations.append(
                PriorityRecommendation(
                    title=alert.recommendation,
                    priority=alert.severity,
                    reason=alert.explanation,
                )
            )
        for risk_item in risk.risks:
            title = {
                "نقص البيانات": "زيادة حجم العينة",
                "ضعف الثقة": "تحسين جودة CISD",
                "ضعف جودة الفرص": "تحسين السيولة",
                "عدم استقرار الجاهزية": "تحسين التوافق العام",
            }.get(risk_item, "تحسين توافق الأطر الزمنية")
            recommendations.append(
                PriorityRecommendation(
                    title=title,
                    priority=risk.severity,
                    reason=f"يرتبط هذا التحسين بالمخاطرة: {risk_item}",
                )
            )
        if not recommendations:
            recommendations.append(
                PriorityRecommendation(
                    title="الاستمرار في المراقبة البحثية",
                    priority="منخفض",
                    reason="لا توجد تنبيهات حرجة في الحالة الحالية.",
                )
            )
        unique: dict[str, PriorityRecommendation] = {}
        for item in recommendations:
            unique.setdefault(item.title, item)
        return tuple(unique.values())


class NextActionEngine:
    """Generate one deterministic next research action."""

    def decide(
        self,
        recommendations: tuple[PriorityRecommendation, ...],
        risk: RiskAssessment,
    ) -> NextAction:
        if recommendations:
            first = recommendations[0]
            return NextAction(
                action=first.title,
                reason=first.reason,
                priority=first.priority,
            )
        return NextAction(
            action="متابعة المراقبة البحثية",
            reason=f"مستوى المخاطر الحالي {risk.severity}.",
            priority="منخفض",
        )
