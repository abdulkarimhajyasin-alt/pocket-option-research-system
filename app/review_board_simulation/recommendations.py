"""Arabic recommendations for review board simulation."""

from __future__ import annotations

from app.review_board_simulation.schemas import SIMULATION_ONLY_FLAGS


class ReviewSimulationRecommendationBuilder:
    """Generate deterministic Arabic recommendations."""

    RECOMMENDATIONS = [
        "إجراء مراجعة حوكمة يدوية قبل أي توسع مستقبلي.",
        "استكمال أدلة المراجعة وربطها بكل بوابة قرار.",
        "معالجة العوائق قبل أي توسع معماري أو تشغيلي.",
        "تقوية معايير مجالس المراجعة وتوثيق مسؤولياتها.",
        "تقوية ربط البوابات بالأدلة المحلية القابلة للتتبع.",
        "تحسين جاهزية مراجعة المخاطر باستخدام أدلة محلية إضافية.",
        "تحسين جاهزية مراجعة الامتثال وربط السياسات بالمخرجات.",
        "تحسين جاهزية مراجعة العمليات وتوثيق سيناريوهات الحوادث.",
        "منع أي انتقال للتنفيذ قبل اجتياز المراجعات المستقبلية الرسمية.",
        "الحفاظ على حدود البحث فقط وعدم إضافة أي تحكم تشغيلي حقيقي.",
    ]

    def build(self) -> list[str]:
        return list(self.RECOMMENDATIONS)

    def as_payload(self) -> dict[str, object]:
        return {"items": self.build(), **SIMULATION_ONLY_FLAGS}
