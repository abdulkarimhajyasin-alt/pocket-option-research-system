"""Analytics for paper control center reports and dashboard."""

from __future__ import annotations

from typing import Any


class PaperControlAnalytics:
    """Generate paper control analysis sections."""

    def summarize(
        self,
        control: Any,
        health: dict[str, Any],
        monitoring: dict[str, Any],
        governance: tuple[Any, ...],
        decision: dict[str, Any],
        diagnostics: tuple[Any, ...],
    ) -> dict[str, Any]:
        governance_distribution: dict[str, int] = {}
        for item in governance:
            governance_distribution[item.status] = governance_distribution.get(item.status, 0) + 1
        warning_distribution: dict[str, int] = {}
        for item in diagnostics:
            warning_distribution[item.name] = warning_distribution.get(item.name, 0) + 1
        return {
            "health_analysis": health,
            "readiness_analysis": {"readiness": health.get("readiness_health", 0.0)},
            "governance_analysis": governance_distribution,
            "execution_analysis": {"execution": health.get("execution_health", 0.0)},
            "portfolio_analysis": {
                "health": control.portfolio_health,
                "stability": control.portfolio_stability,
            },
            "warning_analysis": warning_distribution,
            "monitoring_analysis": monitoring,
            "decision_analysis": {decision.get("arabic_label", "غير متاح"): 1},
            "paper_only": True,
            "research_only": True,
        }
