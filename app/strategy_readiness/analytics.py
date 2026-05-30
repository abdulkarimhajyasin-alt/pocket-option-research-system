"""Analytics for strategy readiness results."""

from __future__ import annotations

from collections import Counter
from typing import Any

from app.strategy_readiness.models import StrategyReadinessResult


class StrategyReadinessAnalytics:
    """Build deterministic analytics from readiness results."""

    def summarize(self, result: StrategyReadinessResult) -> dict[str, Any]:
        gates = result.gates
        diagnostics = result.diagnostics.items
        recommendations = result.recommendations
        failures = [gate for gate in gates if gate.status == "FAIL"]
        return {
            "summary": {
                "readiness_score": result.readiness.score,
                "readiness_state": result.readiness.state,
                "passed_gates": sum(1 for gate in gates if gate.status == "PASS"),
                "warnings": sum(1 for gate in gates if gate.status == "WARNING"),
                "failures": len(failures),
                "stability_score": result.stability.score,
                "recommendation_count": len(recommendations),
                "research_only": True,
            },
            "readiness_distribution": {result.readiness.state: 1},
            "gate_distribution": dict(Counter(gate.status_ar for gate in gates)),
            "failure_distribution": dict(Counter(gate.name for gate in failures)),
            "recommendation_distribution": dict(
                Counter(item.title for item in recommendations)
            ),
            "stability_analysis": result.stability.to_dict(),
            "diagnostics_analysis": dict(Counter(item.severity for item in diagnostics)),
            "strengths": self._strengths(result),
            "weaknesses": self._weaknesses(result),
            "timeline": {result.timestamp.strftime("%H:%M"): result.readiness.score},
            "latest": result.to_dict(),
        }

    def _strengths(self, result: StrategyReadinessResult) -> dict[str, float]:
        return {
            key: value
            for key, value in result.readiness.components.items()
            if value >= 70
        }

    def _weaknesses(self, result: StrategyReadinessResult) -> dict[str, float]:
        return {
            key: value
            for key, value in result.readiness.components.items()
            if value < 70
        }
