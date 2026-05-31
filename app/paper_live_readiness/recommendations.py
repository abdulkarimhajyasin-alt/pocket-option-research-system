"""Arabic recommendations for paper-to-live readiness."""

from __future__ import annotations

from app.paper_live_readiness.models import ReadinessDiagnostic, ReadinessRecommendation


class PaperToLiveRecommendations:
    """Generate Arabic readiness improvement recommendations."""

    DEFAULTS = (
        "زيادة عينة التنفيذ الورقي",
        "تحسين استقرار المحفظة الورقية",
        "تحسين بوابات الجاهزية",
        "تحسين جودة المراقبة",
        "تحسين الاعتماد البحثي",
        "تحسين قيود السلامة",
    )

    def generate(
        self,
        diagnostics: tuple[ReadinessDiagnostic, ...],
    ) -> tuple[ReadinessRecommendation, ...]:
        if not diagnostics:
            return (
                ReadinessRecommendation(
                    title="تحسين قيود السلامة",
                    priority="منخفض",
                    reason="الاستمرار في توثيق أن البوابة جاهزية فقط وليست تنفيذية.",
                ),
            )
        recommendations: list[ReadinessRecommendation] = []
        seen: set[str] = set()
        for item in diagnostics:
            title = item.detail if item.detail in self.DEFAULTS else "تحسين بوابات الجاهزية"
            if title in seen:
                continue
            seen.add(title)
            recommendations.append(
                ReadinessRecommendation(
                    title=title,
                    priority=item.severity,
                    reason=item.name,
                )
            )
        return tuple(recommendations)
