"""Monitoring metrics for paper-only control center."""

from __future__ import annotations

from typing import Any


class PaperMonitoringEngine:
    """Track paper orders, portfolio, drawdown, governance, and readiness changes."""

    def evaluate(self, sources: dict[str, Any]) -> dict[str, Any]:
        execution_latest = self._latest(sources.get("paper_execution", {}))
        portfolio_latest = self._latest(sources.get("paper_portfolio", {}))
        orders = (
            execution_latest.get("orders", [])
            if isinstance(execution_latest, dict)
            else []
        )
        results = (
            execution_latest.get("results", [])
            if isinstance(execution_latest, dict)
            else []
        )
        drawdown = (
            portfolio_latest.get("drawdown", {})
            if isinstance(portfolio_latest, dict)
            else {}
        )
        governance = (
            portfolio_latest.get("governance", []) if isinstance(portfolio_latest, dict) else []
        )
        readiness = self._summary(sources.get("execution_readiness", {}))
        active_orders = sum(1 for item in orders if item.get("status") == "ACTIVE")
        completed_orders = sum(
            1
            for item in orders
            if item.get("status") in {"WIN", "LOSS", "BREAKEVEN", "EXPIRED"}
        )
        governance_warnings = sum(
            1
            for item in governance
            if isinstance(item, dict) and item.get("status") in {"WARNING", "FAIL"}
        )
        drawdown_value = self._score(drawdown.get("maximum_drawdown"))
        readiness_score = self._score(readiness.get("average_readiness"))
        score = max(
            0.0,
            min(
                100.0,
                100.0 - governance_warnings * 8.0 - drawdown_value * 5.0
                + min(10.0, readiness_score / 10.0),
            ),
        )
        return {
            "active_paper_orders": active_orders,
            "completed_paper_orders": completed_orders,
            "paper_result_count": len(results),
            "paper_portfolio_changes": self._score(portfolio_latest.get("score")),
            "drawdown_changes": drawdown_value,
            "governance_changes": governance_warnings,
            "readiness_changes": readiness_score,
            "monitoring_score": round(score, 2),
            "paper_only": True,
        }

    def _latest(self, payload: Any) -> dict[str, Any]:
        if not isinstance(payload, dict):
            return {}
        latest = payload.get("latest", {})
        return latest if isinstance(latest, dict) else {}

    def _summary(self, payload: Any) -> dict[str, Any]:
        if not isinstance(payload, dict):
            return {}
        summary = payload.get("summary", payload)
        return summary if isinstance(summary, dict) else {}

    def _score(self, value: Any) -> float:
        try:
            return max(0.0, min(100.0, float(value)))
        except (TypeError, ValueError):
            return 0.0
