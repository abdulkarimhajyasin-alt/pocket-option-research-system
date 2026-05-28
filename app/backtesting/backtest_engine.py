"""Sequential candle replay backtesting engine."""

from typing import Any

from loguru import logger

from app.backtesting.metrics import MetricsCalculator
from app.backtesting.models import BacktestResult, BacktestTrade, EquityPoint, TradeOutcome
from app.backtesting.simulator import BinaryOptionSimulator
from app.data.models import CandleSeries
from app.risk.risk_engine import RiskEngine
from app.signals.signal import TradeSignal
from app.strategies.base_strategy import BaseStrategy


class BacktestEngine:
    """Replays candles through a strategy and simulates validated signals."""

    def __init__(
        self,
        risk_engine: RiskEngine,
        simulator: BinaryOptionSimulator | None = None,
        metrics_calculator: MetricsCalculator | None = None,
    ) -> None:
        self.risk_engine = risk_engine
        self.simulator = simulator or BinaryOptionSimulator()
        self.metrics_calculator = metrics_calculator or MetricsCalculator()

    def run(self, strategy: BaseStrategy, candles: CandleSeries) -> BacktestResult:
        """Run a backtest using the shared strategy interface."""
        logger.info(
            "Starting backtest for strategy={} candles={}",
            strategy.name,
            len(candles),
        )
        result = BacktestResult(
            symbol=candles.symbol,
            timeframe=candles.timeframe,
            strategy_name=strategy.name,
        )
        equity = 0.0

        for index, candle in enumerate(candles):
            context = self._build_context(candles, index)
            signal = strategy.on_candle(context)
            if signal is None:
                continue

            logger.info("Strategy generated signal at {}: {}", candle.timestamp, signal)
            trade = self._process_signal(signal, candles, index)
            result.trades.append(trade)
            equity += trade.pnl
            result.equity_curve.append(
                EquityPoint(timestamp=candle.timestamp, equity=equity, pnl=trade.pnl)
            )

        metrics = self.metrics_calculator.calculate(result.trades, result.equity_curve)
        result.metrics = metrics.to_dict()
        logger.info("Backtest completed: {}", result.summary())
        return result

    def _build_context(self, candles: CandleSeries, index: int) -> dict[str, Any]:
        return {
            "current_candle": candles[index],
            "history": candles.history_until(index),
            "index": index,
            "series": candles,
        }

    def _process_signal(
        self,
        signal: TradeSignal,
        candles: CandleSeries,
        index: int,
    ) -> BacktestTrade:
        if not self.risk_engine.validate_signal(signal):
            candle = candles[index]
            logger.info("Backtest signal skipped by risk engine at {}", candle.timestamp)
            return BacktestTrade(
                symbol=signal.symbol,
                timeframe=signal.timeframe,
                direction=signal.direction.value,
                strategy_name=signal.strategy_name,
                confidence=signal.confidence,
                entry_timestamp=candle.timestamp,
                entry_price=candle.close,
                exit_timestamp=None,
                exit_price=None,
                outcome=TradeOutcome.SKIPPED,
                pnl=0.0,
                reason="risk_rejected",
            )

        return self.simulator.simulate(signal, candles, index)
