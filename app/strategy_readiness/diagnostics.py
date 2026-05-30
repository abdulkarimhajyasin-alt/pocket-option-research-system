"""Strategy diagnostics engine."""

from __future__ import annotations

from app.strategy_readiness.models import DiagnosticItem, DiagnosticsReport


class StrategyDiagnosticsEngine:
    """Detect weak or unstable strategy research areas."""

    def evaluate(
        self,
        components: dict[str, float],
        gates: tuple,
    ) -> DiagnosticsReport:
        items: list[DiagnosticItem] = []
        checks = {
            "ضعف توليد الإشارات": components.get("جودة الإشارة", 0.0),
            "نموذج الثقة غير مستقر": components.get("دقة الثقة", 0.0),
            "ضعف تأهيل الفرص": components.get("جودة الفرصة", 0.0),
            "تعارض الأطر الزمنية": components.get("جودة الأطر الزمنية", 0.0),
            "ضعف التوافق": components.get("جودة التوافق", 0.0),
            "عدم استقرار دورة الحياة": components.get("جودة دورة الحياة", 0.0),
        }
        for name, score in checks.items():
            if score < 70:
                items.append(
                    DiagnosticItem(
                        name=name,
                        severity=self._severity(score),
                        detail=f"القيمة البحثية الحالية {score:.2f}.",
                    )
                )
        for gate in gates:
            if getattr(gate, "status", "") == "FAIL":
                items.append(
                    DiagnosticItem(
                        name=f"{gate.name} غير مستوفاة",
                        severity="مرتفع",
                        detail=gate.explanation,
                    )
                )
        return DiagnosticsReport(items=tuple(items))

    def _severity(self, score: float) -> str:
        if score < 40:
            return "مرتفع"
        if score < 60:
            return "متوسط"
        return "منخفض"
