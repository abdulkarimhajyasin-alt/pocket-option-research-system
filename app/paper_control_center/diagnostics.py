"""Diagnostics for paper-only control center."""

from __future__ import annotations

from typing import Any

from app.paper_control_center.models import FAIL, WARNING, ControlDiagnostic


class PaperControlDiagnostics:
    """Detect paper control center risks."""

    def evaluate(
        self,
        sources: dict[str, Any],
        health: dict[str, Any],
        governance: tuple[Any, ...],
    ) -> tuple[ControlDiagnostic, ...]:
        diagnostics: list[ControlDiagnostic] = []
        portfolio_latest = self._latest(sources.get("paper_portfolio", {}))
        drawdown = (
            portfolio_latest.get("drawdown", {})
            if isinstance(portfolio_latest, dict)
            else {}
        )
        exposure = (
            portfolio_latest.get("exposure", {})
            if isinstance(portfolio_latest, dict)
            else {}
        )
        if any(item.status == FAIL for item in governance):
            diagnostics.append(
                self._diag("فشل الحوكمة", "مرتفع", "تحسين الحوكمة")
            )
        if self._float(drawdown.get("maximum_drawdown")) > 2.0:
            diagnostics.append(self._diag("سحب مفرط", "مرتفع", "تقليل السحب"))
        if health.get("readiness_health", 0) < 65:
            diagnostics.append(self._diag("جاهزية غير مستقرة", "متوسط", "تحسين الجاهزية"))
        if health.get("execution_health", 0) < 60:
            diagnostics.append(
                self._diag(
                    "تنفيذ ورقي غير مستقر",
                    "متوسط",
                    "تحسين التنفيذ الورقي",
                )
            )
        if self._float(exposure.get("concentration")) > 0.6:
            diagnostics.append(
                self._diag("تركيز المحفظة", "متوسط", "تحسين المحفظة")
            )
        if sum(1 for item in governance if item.status == WARNING) >= 2:
            diagnostics.append(
                self._diag("تحذيرات متكررة", "منخفض", "تحسين الاستقرار")
            )
        return tuple(diagnostics)

    def _latest(self, payload: Any) -> dict[str, Any]:
        latest = payload.get("latest", {}) if isinstance(payload, dict) else {}
        return latest if isinstance(latest, dict) else {}

    def _float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _diag(self, name: str, severity: str, detail: str) -> ControlDiagnostic:
        return ControlDiagnostic(name=name, severity=severity, detail=detail)
