"""Arabic recommendations for platform certification."""

from __future__ import annotations

from typing import Any


class PlatformCertificationRecommendations:
    """Generate certification recommendations."""

    BASE = (
        "تحسين الجودة البحثية",
        "تقوية التغطية المعرفية",
        "تحسين الاتساق",
        "مراجعة التحذيرات",
        "تقوية الأرشفة",
        "تحسين الجاهزية",
        "الحفاظ على حدود البحث فقط",
    )

    def for_domain(self, domain_id: str, diagnostics: list[dict[str, Any]]) -> list[str]:
        if not diagnostics:
            return ["الحفاظ على استقرار المجال البحثي الحالي."]
        mapping = {
            "knowledge_graph": "تقوية التغطية المعرفية",
            "research_archive": "تقوية الأرشفة",
            "readiness": "تحسين الجاهزية",
            "safety": "الحفاظ على حدود البحث فقط",
        }
        return [mapping.get(domain_id, "تحسين الاتساق")]

    def aggregate(self, diagnostics: list[dict[str, Any]]) -> list[str]:
        recommendations = list(self.BASE)
        if not diagnostics:
            recommendations.append("المنصة مؤهلة بحثيا ضمن الحدود المحلية الحالية.")
        return recommendations
