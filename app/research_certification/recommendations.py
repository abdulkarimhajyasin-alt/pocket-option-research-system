"""Certification recommendations."""

from __future__ import annotations

from app.research_certification.models import CertificationRecommendation
from app.research_certification.models import DiagnosticFinding


class CertificationRecommendationEngine:
    """Generate prioritized Arabic certification recommendations."""

    MAP = {
        "حجم عينة غير كاف": "زيادة حجم البيانات",
        "ضعف الثبات": "تحسين الثبات",
        "ضعف الاتساق": "تحسين التوافق",
        "ضعف جودة الأنماط": "تحسين الأنماط",
        "ضعف التكيف مع حالة السوق": "تحسين الأداء عبر حالات السوق",
        "ضعف المتانة": "تحسين الاستقرار",
    }

    def generate(
        self,
        diagnostics: tuple[DiagnosticFinding, ...],
    ) -> tuple[CertificationRecommendation, ...]:
        recommendations = []
        for item in diagnostics:
            title = self.MAP.get(item.name, "تحسين جودة البحث")
            priority = "عالية" if item.severity == "مرتفع" else "متوسطة"
            recommendations.append(
                CertificationRecommendation(title, priority, item.detail)
            )
        if not recommendations:
            recommendations.append(
                CertificationRecommendation(
                    "المتابعة البحثية المستمرة",
                    "منخفضة",
                    "لا توجد عوائق رئيسية لكن يلزم استمرار التحقق البحثي.",
                )
            )
        return tuple(recommendations)
