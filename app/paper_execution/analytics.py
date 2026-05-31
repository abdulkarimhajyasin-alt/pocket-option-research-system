"""Analytics for paper-only execution."""

from __future__ import annotations

from statistics import mean
from typing import Any

from app.paper_execution.models import (
    STATUS_ACTIVE,
    STATUS_BREAKEVEN,
    STATUS_EXPIRED,
    STATUS_LOSS,
    STATUS_REJECTED,
    STATUS_UNRESOLVED,
    STATUS_WIN,
    PaperOrder,
    PaperResult,
)


class PaperExecutionAnalytics:
    """Generate paper execution summary metrics."""

    def summarize(
        self,
        orders: tuple[PaperOrder, ...],
        results: tuple[PaperResult, ...],
    ) -> dict[str, Any]:
        accepted = [item for item in orders if item.status != STATUS_REJECTED]
        wins = [item for item in results if item.outcome == STATUS_WIN]
        losses = [item for item in results if item.outcome == STATUS_LOSS]
        breakeven = [item for item in results if item.outcome == STATUS_BREAKEVEN]
        unresolved = [item for item in results if item.outcome == STATUS_UNRESOLVED]
        returns = [item.simulated_return for item in results]
        drawdown = self._drawdown(returns)
        return {
            "total_paper_orders": len(orders),
            "accepted": len(accepted),
            "rejected": sum(1 for item in orders if item.status == STATUS_REJECTED),
            "active": sum(1 for item in orders if item.status == STATUS_ACTIVE),
            "expired": sum(1 for item in orders if item.status == STATUS_EXPIRED),
            "wins": len(wins),
            "losses": len(losses),
            "breakeven": len(breakeven),
            "unresolved": len(unresolved),
            "win_rate": round(len(wins) / len(results), 4) if results else 0.0,
            "average_confidence": round(mean([item.confidence for item in orders]), 2)
            if orders
            else 0.0,
            "average_readiness": round(mean([item.readiness_score for item in orders]), 2)
            if orders
            else 0.0,
            "paper_drawdown": drawdown,
            "paper_streaks": self._streaks(results),
            "paper_only": True,
            "research_only": True,
            "not_real_execution": True,
        }

    def _drawdown(self, returns: list[float]) -> float:
        equity = 0.0
        peak = 0.0
        max_drawdown = 0.0
        for value in returns:
            equity += value
            peak = max(peak, equity)
            max_drawdown = min(max_drawdown, equity - peak)
        return round(abs(max_drawdown), 2)

    def _streaks(self, results: tuple[PaperResult, ...]) -> dict[str, int]:
        max_win = 0
        max_loss = 0
        current = ""
        count = 0
        for result in results:
            if result.outcome == current:
                count += 1
            else:
                current = result.outcome
                count = 1
            if result.outcome == STATUS_WIN:
                max_win = max(max_win, count)
            if result.outcome == STATUS_LOSS:
                max_loss = max(max_loss, count)
        return {"max_paper_win_streak": max_win, "max_paper_loss_streak": max_loss}
