"""Paper portfolio aggregation engine."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.paper_portfolio.models import PaperPortfolio


class PaperPortfolioEngine:
    """Aggregate paper execution outputs into portfolio statistics."""

    def evaluate(
        self,
        orders: list[dict[str, Any]],
        results: list[dict[str, Any]],
        drawdown: dict[str, Any],
        exposure: dict[str, Any],
        metadata: dict[str, Any],
    ) -> PaperPortfolio:
        wins = sum(1 for item in results if item.get("outcome") == "WIN")
        losses = sum(1 for item in results if item.get("outcome") == "LOSS")
        breakeven = sum(1 for item in results if item.get("outcome") == "BREAKEVEN")
        active = sum(1 for item in orders if item.get("status") == "ACTIVE")
        total_results = len(results)
        win_rate = round(wins / total_results, 4) if total_results else 0.0
        drawdown_score = self._float(drawdown.get("drawdown_score"))
        exposure_score = self._float(exposure.get("exposure_score"))
        stability = self._stability_score(results, drawdown)
        health = round((win_rate * 100 + drawdown_score + stability) / 3, 2)
        risk = round((drawdown_score + exposure_score + stability) / 3, 2)
        return PaperPortfolio(
            portfolio_id="paper_portfolio_0001",
            created_at=datetime.now(UTC).isoformat(),
            total_orders=len(orders),
            active_orders=active,
            wins=wins,
            losses=losses,
            breakeven=breakeven,
            win_rate=win_rate,
            drawdown=self._float(drawdown.get("current_drawdown")),
            stability_score=stability,
            health_score=health,
            risk_score=risk,
            metadata=metadata,
        )

    def _stability_score(
        self,
        results: list[dict[str, Any]],
        drawdown: dict[str, Any],
    ) -> float:
        losses = sum(1 for item in results if item.get("outcome") == "LOSS")
        unresolved = sum(1 for item in results if item.get("outcome") == "UNRESOLVED")
        penalty = losses * 6.0 + unresolved * 3.0 + self._float(
            drawdown.get("maximum_drawdown")
        ) * 10.0
        return round(max(0.0, min(100.0, 100.0 - penalty)), 2)

    def _float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
