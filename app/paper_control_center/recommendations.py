"""Recommendations for paper-only control center."""

from __future__ import annotations

from app.paper_control_center.models import ControlDiagnostic, ControlRecommendation


class PaperControlRecommendations:
    """Generate Arabic paper control center recommendations."""

    def generate(
        self,
        diagnostics: tuple[ControlDiagnostic, ...],
    ) -> tuple[ControlRecommendation, ...]:
        mapping = {
            "فشل الحوكمة": "تحسين الحوكمة",
            "سحب مفرط": "تقليل السحب",
            "جاهزية غير مستقرة": "تحسين الجاهزية",
            "تنفيذ ورقي غير مستقر": "تحسين التنفيذ الورقي",
            "تركيز المحفظة": "تحسين المحفظة",
            "تحذيرات متكررة": "تحسين الاستقرار",
        }
        recommendations = [
            ControlRecommendation(
                title=mapping.get(item.name, "تحسين الاستقرار"),
                priority=item.severity,
                reason=item.detail,
            )
            for item in diagnostics
        ]
        if not recommendations:
            recommendations.append(
                ControlRecommendation(
                    title="تحسين الاستقرار",
                    priority="منخفض",
                    reason="مركز التحكم الورقي مستقر ضمن المراقبة المحلية فقط.",
                )
            )
        return tuple(recommendations)
