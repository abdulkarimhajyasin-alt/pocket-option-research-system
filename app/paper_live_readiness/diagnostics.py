"""Diagnostics for paper-to-live readiness."""

from __future__ import annotations

from typing import Any

from app.paper_live_readiness.models import FAIL, ReadinessDiagnostic


class PaperToLiveDiagnostics:
    """Detect weak readiness areas and safety violations."""

    def evaluate(
        self,
        readiness_scores: dict[str, float],
        gates: tuple[Any, ...],
        safety: dict[str, Any],
        maturity: dict[str, Any],
        stability: dict[str, Any],
    ) -> tuple[ReadinessDiagnostic, ...]:
        diagnostics: list[ReadinessDiagnostic] = []
        if readiness_scores["paper_stability"] < 70 or stability["stability_score"] < 70:
            diagnostics.append(
                self._diag(
                    "ضعف الاستقرار الورقي",
                    "مرتفع",
                    "تحسين استقرار المحفظة الورقية",
                )
            )
        if readiness_scores["paper_governance"] < 75:
            diagnostics.append(self._diag("ضعف الحوكمة", "مرتفع", "تحسين بوابات الجاهزية"))
        if readiness_scores["certification_score"] < 70:
            diagnostics.append(self._diag("ضعف الاعتماد البحثي", "متوسط", "تحسين الاعتماد البحثي"))
        if readiness_scores["observation_readiness"] < 70:
            diagnostics.append(self._diag("ضعف جاهزية المراقبة", "متوسط", "تحسين جودة المراقبة"))
        if readiness_scores["execution_readiness"] < 70:
            diagnostics.append(self._diag("ضعف جاهزية التنفيذ", "متوسط", "تحسين بوابات الجاهزية"))
        if safety.get("status") == FAIL:
            diagnostics.append(self._diag("مخالفة سلامة", "مرتفع", "تحسين قيود السلامة"))
        if maturity.get("paper_sample_maturity", 0) < 70:
            diagnostics.append(
                self._diag(
                    "عينة ورقية غير كافية",
                    "منخفض",
                    "زيادة عينة التنفيذ الورقي",
                )
            )
        if any(item.status == FAIL for item in gates) and not diagnostics:
            diagnostics.append(self._diag("فشل بوابة", "متوسط", "تحسين بوابات الجاهزية"))
        return tuple(diagnostics)

    def _diag(self, name: str, severity: str, detail: str) -> ReadinessDiagnostic:
        return ReadinessDiagnostic(name=name, severity=severity, detail=detail)
