"""Analytics for simulated execution results."""

from __future__ import annotations

from collections import Counter
from statistics import mean
from typing import Any

from app.execution_simulator.models import BinaryOutcome, SimulatedTrade


class SimulationAnalytics:
    """Build deterministic analytics from simulated trades."""

    def summarize(self, trades: list[SimulatedTrade]) -> dict[str, Any]:
        """Return execution simulation analytics."""
        executed = [
            trade
            for trade in trades
            if trade.outcome in {BinaryOutcome.WIN, BinaryOutcome.LOSS, BinaryOutcome.DRAW}
        ]
        wins = sum(1 for trade in executed if trade.outcome == BinaryOutcome.WIN)
        losses = sum(1 for trade in executed if trade.outcome == BinaryOutcome.LOSS)
        draws = sum(1 for trade in executed if trade.outcome == BinaryOutcome.DRAW)
        blocked = [trade for trade in trades if trade.outcome == BinaryOutcome.BLOCKED]
        total_executed = len(executed)
        profit_loss = round(sum(trade.profit_loss for trade in trades), 8)
        returns = [trade.actual_return for trade in executed]
        confidences = [trade.confidence for trade in trades]
        return {
            "total_trades": len(trades),
            "executed_trades": total_executed,
            "wins": wins,
            "losses": losses,
            "draws": draws,
            "blocked_trades": len(blocked),
            "skipped_trades": sum(
                1 for trade in trades if trade.outcome == BinaryOutcome.SKIPPED
            ),
            "win_rate": round(wins / total_executed, 4) if total_executed else 0.0,
            "loss_rate": round(losses / total_executed, 4) if total_executed else 0.0,
            "profit_loss": profit_loss,
            "expectancy": round(profit_loss / total_executed, 8)
            if total_executed
            else 0.0,
            "average_return": round(mean(returns), 8) if returns else 0.0,
            "average_confidence": round(mean(confidences), 4) if confidences else 0.0,
            "streaks": self._streaks(executed),
            "payout": self._payout_analysis(executed),
            "confidence_distribution": self._confidence_distribution(confidences),
            "blocked_by_rule": dict(Counter(trade.blocked_reason for trade in blocked)),
        }

    def _streaks(self, trades: list[SimulatedTrade]) -> dict[str, int]:
        max_win = 0
        max_loss = 0
        current_outcome: BinaryOutcome | None = None
        current_count = 0
        for trade in trades:
            if trade.outcome == current_outcome:
                current_count += 1
            else:
                current_outcome = trade.outcome
                current_count = 1
            if trade.outcome == BinaryOutcome.WIN:
                max_win = max(max_win, current_count)
            if trade.outcome == BinaryOutcome.LOSS:
                max_loss = max(max_loss, current_count)
        return {"max_win_streak": max_win, "max_loss_streak": max_loss}

    def _payout_analysis(self, trades: list[SimulatedTrade]) -> dict[str, float]:
        payouts = [trade.payout for trade in trades]
        losses = [abs(trade.profit_loss) for trade in trades if trade.profit_loss < 0]
        return {
            "total_payout": round(sum(payouts), 8),
            "average_payout": round(mean(payouts), 8) if payouts else 0.0,
            "total_loss": round(sum(losses), 8),
        }

    def _confidence_distribution(self, confidences: list[float]) -> dict[str, int]:
        buckets = {"منخفضة": 0, "متوسطة": 0, "مرتفعة": 0}
        for confidence in confidences:
            if confidence < 0.6:
                buckets["منخفضة"] += 1
            elif confidence < 0.75:
                buckets["متوسطة"] += 1
            else:
                buckets["مرتفعة"] += 1
        return buckets
