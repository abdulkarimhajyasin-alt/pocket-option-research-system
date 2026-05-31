"""Arabic architecture hardening recommendations."""

from __future__ import annotations

from app.architecture_audit.models import (
    ArchitectureDiagnostic,
    ArchitectureRecommendation,
)


class ArchitectureRecommendations:
    """Generate remediation recommendations for cleanup and hardening."""

    TITLES = {
        "تنظيف البنية",
        "تعزيز السلامة",
        "تحسين الأداء",
        "تحسين الاتساق",
        "تحسين القابلية للصيانة",
        "تعزيز الاختبارات",
    }

    def generate(
        self,
        diagnostics: tuple[ArchitectureDiagnostic, ...],
    ) -> tuple[ArchitectureRecommendation, ...]:
        recommendations: list[ArchitectureRecommendation] = []
        seen: set[str] = set()
        for item in diagnostics:
            title = item.detail if item.detail in self.TITLES else "تعزيز السلامة"
            if title in seen:
                continue
            seen.add(title)
            recommendations.append(
                ArchitectureRecommendation(
                    title=title,
                    priority=item.severity,
                    reason=item.name,
                )
            )
        return tuple(recommendations)
