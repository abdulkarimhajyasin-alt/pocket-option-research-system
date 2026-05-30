"""Deterministic strategy improvement recommendations."""

from __future__ import annotations

from app.strategy_readiness.models import DiagnosticsReport, Recommendation


class RecommendationEngine:
    """Generate Arabic deterministic improvement recommendations."""

    def generate(
        self,
        components: dict[str, float],
        diagnostics: DiagnosticsReport,
    ) -> tuple[Recommendation, ...]:
        recommendations: list[Recommendation] = []
        mapping = [
            ("جودة الإشارة", "تحسين جودة CISD", "رفع جودة توليد الإشارات"),
            ("جودة الأطر الزمنية", "تحسين توافق الأطر الزمنية", "تقليل التعارض الزمني"),
            ("دقة الثقة", "تحسين الثقة", "زيادة موثوقية نموذج الثقة"),
            ("جودة الفرصة", "تحسين جودة السيولة", "رفع جودة تأهيل الفرص"),
            ("جودة دورة الحياة", "زيادة حجم العينة", "تحسين استقرار دورة الحياة"),
        ]
        for key, title, reason in mapping:
            score = components.get(key, 0.0)
            if score < 70:
                recommendations.append(
                    Recommendation(
                        title=title,
                        priority=self._priority(score),
                        reason=reason,
                    )
                )
        if not recommendations and not diagnostics.items:
            recommendations.append(
                Recommendation(
                    title="الاستمرار في المراقبة البحثية",
                    priority="منخفض",
                    reason="لا توجد فجوات حرجة في التقييم الحالي",
                )
            )
        return tuple(recommendations)

    def _priority(self, score: float) -> str:
        if score < 45:
            return "مرتفع"
        if score < 60:
            return "متوسط"
        return "منخفض"
