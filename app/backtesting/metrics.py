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
    ) -> PerformanceMetrics:
        """Calculate structured performance metrics."""
        executed = [trade for trade in trades if trade.outcome != TradeOutcome.SKIPPED]
        wins = sum(1 for trade in trades if trade.outcome == TradeOutcome.WIN)
        losses = sum(1 for trade in trades if trade.outcome == TradeOutcome.LOSS)
        skipped = sum(1 for trade in trades if trade.outcome == TradeOutcome.SKIPPED)
        gross_profit = sum(trade.pnl for trade in trades if trade.pnl > 0)
        gross_loss = abs(sum(trade.pnl for trade in trades if trade.pnl < 0))
        win_rate = wins / len(executed) if executed else 0.0
        profit_factor = gross_profit / gross_loss if gross_loss else float(gross_profit > 0)
        net_pnl = sum(trade.pnl for trade in trades)

        metrics = PerformanceMetrics(
            total_trades=len(executed),
            wins=wins,
            losses=losses,
            skipped=skipped,
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
