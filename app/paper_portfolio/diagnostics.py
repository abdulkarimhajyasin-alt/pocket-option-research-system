"""Diagnostics and recommendations for paper portfolio governance."""

from __future__ import annotations

from typing import Any

from app.paper_portfolio.models import FAIL, WARNING, PortfolioDiagnostic, PortfolioRecommendation


class PaperPortfolioDiagnostics:
    """Detect portfolio-level paper-only risks."""

    def evaluate(
        self,
        portfolio: Any,
        exposure: dict[str, Any],
        drawdown: dict[str, Any],
        governance: tuple[Any, ...],
        limits: tuple[Any, ...],
    ) -> tuple[PortfolioDiagnostic, ...]:
        diagnostics: list[PortfolioDiagnostic] = []
        if float(drawdown.get("maximum_drawdown", 0.0)) > 2.0:
            diagnostics.append(self._diagnostic("سحب مفرط", "مرتفع", "تقليل السحب"))
        if portfolio.stability_score < 70:
            diagnostics.append(self._diagnostic("محفظة غير مستقرة", "متوسط", "تحسين الاستقرار"))
        if float(exposure.get("concentration", 0.0)) > 0.6:
            diagnostics.append(self._diagnostic("تركيز مرتفع", "متوسط", "تقليل التركيز"))
        if portfolio.health_score < 70:
            diagnostics.append(self._diagnostic("جودة ضعيفة", "متوسط", "تحسين الجودة"))
        if any(item.status in {WARNING, FAIL} for item in governance + limits):
            diagnostics.append(self._diagnostic("تحذيرات حوكمة", "مرتفع", "تقليل التعرض"))
        return tuple(diagnostics)

    def _diagnostic(self, name: str, severity: str, detail: str) -> PortfolioDiagnostic:
        return PortfolioDiagnostic(name=name, severity=severity, detail=detail)


class PaperPortfolioRecommendations:
    """Generate Arabic recommendations for paper portfolio governance."""

    def generate(
        self,
        diagnostics: tuple[PortfolioDiagnostic, ...],
    ) -> tuple[PortfolioRecommendation, ...]:
        mapping = {
            "سحب مفرط": "تقليل السحب",
            "محفظة غير مستقرة": "تحسين الاستقرار",
            "تركيز مرتفع": "تقليل التركيز",
            "جودة ضعيفة": "تحسين الجودة",
            "تحذيرات حوكمة": "تقليل التعرض",
        }
        recommendations = [
            PortfolioRecommendation(
                title=mapping.get(item.name, "تحسين الجاهزية"),
                priority=item.severity,
                reason=item.detail,
            )
            for item in diagnostics
        ]
        if not recommendations:
            recommendations.append(
                PortfolioRecommendation(
                    title="تحسين الاستقرار",
                    priority="منخفض",
                    reason="المحفظة الورقية مستقرة ضمن المحاكاة المحلية فقط.",
                )
            )
        return tuple(recommendations)
