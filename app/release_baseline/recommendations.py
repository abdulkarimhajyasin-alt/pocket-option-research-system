"""Arabic recommendations for release baseline reconciliation."""

from __future__ import annotations


class ReleaseBaselineRecommendationBuilder:
    """Generate deterministic Arabic baseline recommendations."""

    RECOMMENDATIONS = [
        "مراجعة خط الأساس قبل commit.",
        "تحديد الملفات التي يجب تضمينها في الإصدار بقرار بشري.",
        "فصل ملفات الأدلة عن الملفات المؤقتة.",
        "عدم حذف الملفات تلقائياً.",
        "مراجعة ملفات phase المحذوفة أو غير المتتبعة.",
        "مراجعة artifacts الناتجة عن validation قبل commit.",
        "اعتماد سياسة واضحة للـ reports و storage.",
        "تحديث .gitignore بعد موافقة بشرية فقط.",
        "إجراء commit فقط بعد مراجعة checklist.",
        "الحفاظ على حدود البحث فقط دون تشغيل حقيقي.",
    ]

    def build(self) -> list[str]:
        return list(self.RECOMMENDATIONS)
