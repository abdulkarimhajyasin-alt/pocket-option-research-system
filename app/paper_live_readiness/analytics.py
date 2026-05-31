"""Analytics for paper-to-live readiness reports."""

from __future__ import annotations

from typing import Any

from app.paper_live_readiness.models import PaperToLiveReadiness, ReadinessGate


class PaperToLiveAnalytics:
    """Build structured readiness analytics for reports and dashboard loading."""

    def summarize(
        self,
        readiness: PaperToLiveReadiness,
        gates: tuple[ReadinessGate, ...],
        safety: dict[str, Any],
        maturity: dict[str, Any],
        stability: dict[str, Any],
        diagnostics: tuple[Any, ...],
    ) -> dict[str, Any]:
        gate_distribution: dict[str, int] = {}
        for item in gates:
            gate_distribution[item.status] = gate_distribution.get(item.status, 0) + 1
        return {
            "readiness_distribution": {
                "paper_health": readiness.paper_health,
                "paper_stability": readiness.paper_stability,
                "paper_governance": readiness.paper_governance,
                "execution_readiness": readiness.execution_readiness,
                "observation_readiness": readiness.observation_readiness,
                "certification_score": readiness.certification_score,
            },
            "gate_distribution": gate_distribution,
            "stability": stability,
            "maturity": maturity,
            "safety": safety,
            "paper": {
                "health": readiness.paper_health,
                "stability": readiness.paper_stability,
                "governance": readiness.paper_governance,
            },
            "observation": {"readiness": readiness.observation_readiness},
            "certification": {"score": readiness.certification_score},
            "warnings": {"diagnostics": len(diagnostics)},
            "readiness_only": True,
        }
