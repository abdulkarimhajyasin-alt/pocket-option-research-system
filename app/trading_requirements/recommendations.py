"""Arabic recommendations for trading requirements specification."""

from __future__ import annotations


class TradingRequirementsRecommendationBuilder:
    """Build deterministic Arabic recommendations."""

    def build(self) -> list[str]:
        return [
            "استكمال توثيق المتطلبات",
            "فصل المتطلبات عن التنفيذ",
            "مراجعة القيود القانونية",
            "مراجعة شروط الوسيط",
            "تقوية متطلبات المخاطر",
            "تقوية متطلبات المراقبة",
            "تعريف بوابات الموافقة",
            "منع أي تنفيذ مباشر قبل اكتمال المتطلبات",
            "الحفاظ على حدود البحث فقط",
            "نقل أي تنفيذ مستقبلي إلى برنامج منفصل بعد الموافقات",
        ]
