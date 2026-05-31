"""Diagnostics for architecture audit."""

from __future__ import annotations

from typing import Any

from app.architecture_audit.models import ArchitectureDiagnostic


class ArchitectureDiagnostics:
    """Detect duplication, inconsistency, stale outputs, weak safety, and gaps."""

    def evaluate(
        self,
        architecture: dict[str, Any],
        consistency: dict[str, Any],
        dependency: dict[str, Any],
        performance: dict[str, Any],
        safety: dict[str, Any],
        test_count: int,
    ) -> tuple[ArchitectureDiagnostic, ...]:
        diagnostics: list[ArchitectureDiagnostic] = []
        if dependency.get("duplicated_logic_indicator", 0) > 20:
            diagnostics.append(self._diag("تكرار منطقي", "منخفض", "تحسين القابلية للصيانة"))
        if consistency.get("missing_storage_counterparts"):
            diagnostics.append(self._diag("عدم اتساق", "متوسط", "تحسين الاتساق"))
        if performance.get("report_count", 0) > 250:
            diagnostics.append(self._diag("تقارير كثيرة", "منخفض", "تحسين الأداء"))
        if safety.get("missing_safety_flags") or safety.get("risky_imports"):
            diagnostics.append(self._diag("بيانات سلامة ضعيفة", "مرتفع", "تعزيز السلامة"))
        if architecture.get("missing_packages"):
            diagnostics.append(self._diag("حزم مفقودة", "مرتفع", "تنظيف البنية"))
        if test_count < 20:
            diagnostics.append(self._diag("اختبارات ناقصة", "متوسط", "تعزيز الاختبارات"))
        if not diagnostics:
            diagnostics.append(self._diag("مراجعة دورية مطلوبة", "منخفض", "تعزيز السلامة"))
        return tuple(diagnostics)

    def _diag(self, name: str, severity: str, detail: str) -> ArchitectureDiagnostic:
        return ArchitectureDiagnostic(name=name, severity=severity, detail=detail)
