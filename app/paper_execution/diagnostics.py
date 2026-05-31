"""Diagnostics and recommendations for paper execution."""

from __future__ import annotations

from app.paper_execution.models import (
    RISK_FAIL,
    RISK_WARNING,
    STATUS_LOSS,
    STATUS_REJECTED,
    STATUS_UNRESOLVED,
    PaperExecutionDiagnostic,
    PaperExecutionRecommendation,
    PaperOrder,
    PaperResult,
    PaperRiskGate,
)


class PaperExecutionDiagnostics:
    """Detect paper-only execution issues."""

    def evaluate(
        self,
        orders: tuple[PaperOrder, ...],
        results: tuple[PaperResult, ...],
        risk_gates: tuple[PaperRiskGate, ...],
        analytics: dict[str, object],
    ) -> tuple[PaperExecutionDiagnostic, ...]:
        diagnostics: list[PaperExecutionDiagnostic] = []
        if any(item.readiness_score < 70 for item in orders):
            diagnostics.append(self._diagnostic("مرشحون ضعفاء", "متوسط", "تحسين الجاهزية"))
        if any(item.status == STATUS_REJECTED for item in orders):
            diagnostics.append(self._diagnostic("أوامر مرفوضة", "متوسط", "تقليل الإشارات الضعيفة"))
        if any(item.outcome == STATUS_UNRESOLVED for item in results):
            diagnostics.append(self._diagnostic("نتائج غير محسومة", "منخفض", "تحسين الاستقرار"))
        if any(item.status in {RISK_WARNING, RISK_FAIL} for item in risk_gates):
            diagnostics.append(
                self._diagnostic(
                    "تحذيرات مخاطر ورقية",
                    "مرتفع",
                    "تحسين قواعد المخاطر الورقية",
                )
            )
        if float(analytics.get("average_readiness", 0.0)) < 75:
            diagnostics.append(
                self._diagnostic("جاهزية ضعيفة", "متوسط", "تحسين الجاهزية")
            )
        if float(analytics.get("win_rate", 0.0)) < 0.4 and results:
            diagnostics.append(
                self._diagnostic(
                    "نتائج ورقية غير مستقرة",
                    "مرتفع",
                    "تحسين الاستقرار",
                )
            )
        if any(item.outcome == STATUS_LOSS for item in results):
            diagnostics.append(
                self._diagnostic("خسائر ورقية", "منخفض", "تحسين جودة المرشحين")
            )
        return tuple(diagnostics)

    def _diagnostic(
        self,
        name: str,
        severity: str,
        detail: str,
    ) -> PaperExecutionDiagnostic:
        return PaperExecutionDiagnostic(name=name, severity=severity, detail=detail)


class PaperExecutionRecommendations:
    """Generate Arabic recommendations for paper execution."""

    def generate(
        self,
        diagnostics: tuple[PaperExecutionDiagnostic, ...],
    ) -> tuple[PaperExecutionRecommendation, ...]:
        mapping = {
            "مرشحون ضعفاء": "تحسين الجاهزية",
            "أوامر مرفوضة": "تقليل الإشارات الضعيفة",
            "نتائج غير محسومة": "تحسين الاستقرار",
            "تحذيرات مخاطر ورقية": "تحسين قواعد المخاطر الورقية",
            "جاهزية ضعيفة": "تحسين الثقة",
            "نتائج ورقية غير مستقرة": "تحسين الاستقرار",
            "خسائر ورقية": "تحسين جودة المرشحين",
        }
        recommendations = [
            PaperExecutionRecommendation(
                title=mapping.get(item.name, "تحسين الجاهزية"),
                priority=item.severity,
                reason=item.detail,
            )
            for item in diagnostics
        ]
        if not recommendations:
            recommendations.append(
                PaperExecutionRecommendation(
                    title="المتابعة الورقية",
                    priority="منخفض",
                    reason="نتائج الورق مستقرة ضمن المحاكاة المحلية فقط.",
                )
            )
        return tuple(recommendations)
