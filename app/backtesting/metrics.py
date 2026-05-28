"""Backtesting performance metrics."""

from dataclasses import asdict, dataclass

from loguru import logger

from app.backtesting.models import BacktestTrade, EquityPoint, TradeOutcome


@dataclass(frozen=True)
class PerformanceMetrics:
    """Structured performance metrics for a backtest run."""

    total_trades: int
    wins: int
    losses: int
    skipped: int
    blocked_trades: int
    rejection_rate: float
    average_streak_length: float
    cooldown_frequency: float
    exposure_active_trades: int
    win_rate: float
    profit_factor: float
    max_drawdown: float
    consecutive_losses: int
    net_pnl: float

    def to_dict(self) -> dict[str, float | int]:
        """Return metrics as a serializable dictionary."""
        return asdict(self)


class MetricsCalculator:
    """Calculates performance metrics from simulated trades."""

    def calculate(
        self,
        trades: list[BacktestTrade],
        equity_curve: list[EquityPoint],
        risk_summary: dict[str, object] | None = None,
    ) -> PerformanceMetrics:
        """Calculate structured performance metrics."""
        risk_summary = risk_summary or {}
        executed = [
            trade
            for trade in trades
            if trade.outcome not in {TradeOutcome.SKIPPED, TradeOutcome.BLOCKED}
        ]
        wins = sum(1 for trade in trades if trade.outcome == TradeOutcome.WIN)
        losses = sum(1 for trade in trades if trade.outcome == TradeOutcome.LOSS)
        skipped = sum(1 for trade in trades if trade.outcome == TradeOutcome.SKIPPED)
        blocked = sum(1 for trade in trades if trade.outcome == TradeOutcome.BLOCKED)
        gross_profit = sum(trade.pnl for trade in trades if trade.pnl > 0)
        gross_loss = abs(sum(trade.pnl for trade in trades if trade.pnl < 0))
        win_rate = wins / len(executed) if executed else 0.0
        profit_factor = gross_profit / gross_loss if gross_loss else float(gross_profit > 0)
        net_pnl = sum(trade.pnl for trade in trades)
        signal_count = len(trades)
        rejection_rate = blocked / signal_count if signal_count else 0.0
        cooldown_events = int(risk_summary.get("cooldown_event_count", 0))
        risk_state = risk_summary.get("risk_state", {})
        exposure = risk_state.get("exposure", {}) if isinstance(risk_state, dict) else {}
        active_trades = int(exposure.get("active_trades", 0)) if isinstance(exposure, dict) else 0

        metrics = PerformanceMetrics(
            total_trades=len(executed),
            wins=wins,
            losses=losses,
            skipped=skipped,
            blocked_trades=blocked,
            rejection_rate=round(rejection_rate, 4),
            average_streak_length=round(self._average_loss_streak_length(trades), 4),
            cooldown_frequency=round(cooldown_events / signal_count, 4) if signal_count else 0.0,
            exposure_active_trades=active_trades,
            win_rate=round(win_rate, 4),
            profit_factor=round(profit_factor, 4),
            max_drawdown=round(self._max_drawdown(equity_curve), 4),
            consecutive_losses=self._max_consecutive_losses(trades),
            net_pnl=round(net_pnl, 4),
        )
        logger.info("Generated backtest metrics: {}", metrics.to_dict())
        return metrics

    def _max_drawdown(self, equity_curve: list[EquityPoint]) -> float:
        peak = 0.0
        max_drawdown = 0.0

        for point in equity_curve:
            peak = max(peak, point.equity)
            drawdown = peak - point.equity
            max_drawdown = max(max_drawdown, drawdown)

        return max_drawdown

    def _max_consecutive_losses(self, trades: list[BacktestTrade]) -> int:
        current = 0
        maximum = 0

        for trade in trades:
            if trade.outcome == TradeOutcome.LOSS:
                current += 1
                maximum = max(maximum, current)
            elif trade.outcome == TradeOutcome.WIN:
                current = 0

        return maximum

    def _average_loss_streak_length(self, trades: list[BacktestTrade]) -> float:
        streaks: list[int] = []
        current = 0

        for trade in trades:
            if trade.outcome == TradeOutcome.LOSS:
                current += 1
                continue
            if current:
                streaks.append(current)
                current = 0

        if current:
            streaks.append(current)
        return sum(streaks) / len(streaks) if streaks else 0.0
