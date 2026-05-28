"""Research-grade performance analysis from journal and equity data."""

from datetime import UTC, datetime

from loguru import logger

from app.analytics.equity_curve import EquityCurveTracker
from app.analytics.models import AnalyticsSnapshot, RuntimePerformance, TradeJournalEntry
from app.analytics.session_analytics import SessionAnalytics
from app.analytics.symbol_analytics import SymbolAnalytics


class PerformanceAnalyzer:
    """Creates reusable analytics snapshots from journal entries."""

    def __init__(
        self,
        session_analytics: SessionAnalytics | None = None,
        symbol_analytics: SymbolAnalytics | None = None,
    ) -> None:
        self.session_analytics = session_analytics or SessionAnalytics()
        self.symbol_analytics = symbol_analytics or SymbolAnalytics()

    def analyze(
        self,
        entries: list[TradeJournalEntry],
        equity_curve: EquityCurveTracker | None = None,
        runtime_performance: RuntimePerformance | None = None,
    ) -> AnalyticsSnapshot:
        """Return a structured analytics snapshot."""
        settled = [entry for entry in entries if entry.lifecycle_state == "settled"]
        snapshot = AnalyticsSnapshot(
            generated_at=datetime.now(tz=UTC),
            trade_count=len(settled),
            net_pnl=round(sum(entry.pnl for entry in settled), 4),
            max_drawdown=round(equity_curve.max_drawdown if equity_curve else 0.0, 4),
            strategy_performance=self._strategy_performance(entries),
            symbol_performance=self.symbol_analytics.analyze(entries),
            session_performance=self.session_analytics.analyze(entries),
            hourly_performance=self._hourly_performance(entries),
            rejection_analysis=self._rejection_analysis(entries),
            streak_analysis=self._streak_analysis(settled),
            exposure_analysis=self._exposure_analysis(entries),
            runtime_performance=runtime_performance,
        )
        logger.bind(component="analytics").info(
            "Analytics snapshot generated trades={} net_pnl={}",
            snapshot.trade_count,
            snapshot.net_pnl,
        )
        return snapshot

    def _strategy_performance(
        self,
        entries: list[TradeJournalEntry],
    ) -> dict[str, dict[str, float | int]]:
        results: dict[str, dict[str, float | int]] = {}
        for strategy in sorted({entry.strategy_name for entry in entries}):
            strategy_entries = [entry for entry in entries if entry.strategy_name == strategy]
            settled = [entry for entry in strategy_entries if entry.lifecycle_state == "settled"]
            wins = sum(1 for entry in settled if entry.outcome == "win")
            losses = sum(1 for entry in settled if entry.outcome == "loss")
            results[strategy] = {
                "trades": len(settled),
                "wins": wins,
                "losses": losses,
                "win_rate": round(wins / len(settled), 4) if settled else 0.0,
                "pnl": round(sum(entry.pnl for entry in settled), 4),
                "blocked": sum(
                    1 for entry in strategy_entries if entry.lifecycle_state == "blocked"
                ),
            }
        return results

    def _hourly_performance(
        self,
        entries: list[TradeJournalEntry],
    ) -> dict[int, dict[str, float | int]]:
        results: dict[int, dict[str, float | int]] = {}
        for hour in range(24):
            hour_entries = [
                entry
                for entry in entries
                if entry.timestamp.astimezone(UTC).hour == hour
                and entry.lifecycle_state == "settled"
            ]
            results[hour] = {
                "trades": len(hour_entries),
                "wins": sum(1 for entry in hour_entries if entry.outcome == "win"),
                "losses": sum(1 for entry in hour_entries if entry.outcome == "loss"),
                "pnl": round(sum(entry.pnl for entry in hour_entries), 4),
            }
        return results

    def _rejection_analysis(self, entries: list[TradeJournalEntry]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for entry in entries:
            if entry.lifecycle_state != "blocked":
                continue
            reason = entry.rejection_reason or "unknown"
            counts[reason] = counts.get(reason, 0) + 1
        return counts

    def _streak_analysis(self, settled: list[TradeJournalEntry]) -> dict[str, int | float]:
        max_loss_streak = 0
        current_loss_streak = 0
        loss_streaks: list[int] = []
        for entry in settled:
            if entry.outcome == "loss":
                current_loss_streak += 1
                max_loss_streak = max(max_loss_streak, current_loss_streak)
            else:
                if current_loss_streak:
                    loss_streaks.append(current_loss_streak)
                current_loss_streak = 0
        if current_loss_streak:
            loss_streaks.append(current_loss_streak)
        return {
            "max_consecutive_losses": max_loss_streak,
            "average_loss_streak": round(sum(loss_streaks) / len(loss_streaks), 4)
            if loss_streaks
            else 0.0,
        }

    def _exposure_analysis(self, entries: list[TradeJournalEntry]) -> dict[str, int]:
        exposure: dict[str, int] = {}
        for entry in entries:
            if entry.lifecycle_state != "executed":
                continue
            key = f"{entry.symbol}:{entry.direction}:{entry.strategy_name}"
            exposure[key] = exposure.get(key, 0) + 1
        return exposure
