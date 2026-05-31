"""Arabic recommendations for integration safety boundary."""

from __future__ import annotations

from app.integration_safety.models import SafetyDiagnostic, SafetyRecommendation


class IntegrationSafetyRecommendations:
    """Generate Arabic safety recommendations."""

    ALLOWED = {
        "تعزيز حدود الأمان",
        "تحسين بيانات السلامة",
        "توضيح القدرات المسموحة",
        "توضيح القدرات المحظورة",
        "تحسين سجل التدقيق",
        "تقوية طبقة العزل",
    }

    def generate(
        self,
        diagnostics: tuple[SafetyDiagnostic, ...],
    ) -> tuple[SafetyRecommendation, ...]:
        recommendations: list[SafetyRecommendation] = []
        seen: set[str] = set()
        for item in diagnostics:
            title = item.detail if item.detail in self.ALLOWED else "تعزيز حدود الأمان"
            if title in seen:
                continue
            seen.add(title)
            recommendations.append(
                SafetyRecommendation(
                    title=title,
                    priority=item.severity,
                    reason=item.name,
                )
            )
        if not recommendations:
            recommendations.append(
                SafetyRecommendation(
                    title="تقوية طبقة العزل",
                    priority="منخفض",
                    reason="مراجعة دورية للحدود المسموحة والمحظورة.",
                )
            )
        return tuple(recommendations)
