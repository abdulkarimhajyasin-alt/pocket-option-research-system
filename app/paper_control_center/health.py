"""Health scoring for paper-only control center."""

from __future__ import annotations

from typing import Any


class PaperHealthEngine:
    """Evaluate paper portfolio, execution, readiness, governance, and stability."""

    def evaluate(self, sources: dict[str, Any]) -> dict[str, Any]:
        portfolio = sources.get("paper_portfolio", {})
        execution = sources.get("paper_execution", {})
        readiness = sources.get("execution_readiness", {})
        portfolio_summary = self._summary(portfolio)
        execution_summary = self._summary(execution)
        readiness_summary = self._summary(readiness)
        portfolio_health = self._score(portfolio_summary.get("health_score"))
        execution_health = self._score(execution_summary.get("paper_execution_score"))
        readiness_health = self._score(readiness_summary.get("average_readiness"))
        governance_health = self._governance_score(portfolio)
        stability_health = self._score(portfolio_summary.get("stability_score"))
        score = self._average(
            [
                portfolio_health,
                execution_health,
                readiness_health,
                governance_health,
                stability_health,
            ]
        )
        return {
            "portfolio_health": portfolio_health,
            "execution_health": execution_health,
            "readiness_health": readiness_health,
            "governance_health": governance_health,
            "stability_health": stability_health,
            "health_score": score,
            "paper_only": True,
        }

    def _summary(self, payload: Any) -> dict[str, Any]:
        if not isinstance(payload, dict):
            return {}
        summary = payload.get("summary", payload)
        return summary if isinstance(summary, dict) else {}

    def _governance_score(self, payload: Any) -> float:
        latest = payload.get("latest", {}) if isinstance(payload, dict) else {}
        governance = latest.get("governance", []) if isinstance(latest, dict) else []
        limits = latest.get("limits", []) if isinstance(latest, dict) else []
        scores = [
            self._score(item.get("score"))
            for item in [*governance, *limits]
            if isinstance(item, dict)
        ]
        return self._average(scores, default=75.0)

    def _score(self, value: Any) -> float:
        try:
            return round(max(0.0, min(100.0, float(value))), 2)
        except (TypeError, ValueError):
            return 0.0

    def _average(self, values: list[float], default: float = 0.0) -> float:
        numeric = [value for value in values if value is not None]
        return round(sum(numeric) / len(numeric), 2) if numeric else default
