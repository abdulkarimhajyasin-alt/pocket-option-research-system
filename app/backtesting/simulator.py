"""Trade outcome simulator for binary-option style backtests."""

from dataclasses import dataclass

from loguru import logger

from app.backtesting.models import BacktestTrade, TradeOutcome
from app.data.models import CandleSeries
from app.signals.signal import SignalDirection, TradeSignal


@dataclass(frozen=True)
class BinaryOptionSimulator:
    """Simulates fixed-stake binary-option style outcomes."""

    payout_percentage: float = 0.80
    expiry_candles: int = 1
    stake: float = 1.0

    def simulate(
        self,
        signal: TradeSignal,
        candles: CandleSeries,
        entry_index: int,
    ) -> BacktestTrade:
        """Simulate one signal outcome using future candle close prices."""
        expiry_index = entry_index + self.expiry_candles
        entry_candle = candles[entry_index]

        if expiry_index >= len(candles):
            logger.info("Trade skipped: insufficient future candles at index {}", entry_index)
            return BacktestTrade(
                symbol=signal.symbol,
                timeframe=signal.timeframe,
                direction=signal.direction.value,
                strategy_name=signal.strategy_name,
                confidence=signal.confidence,
                entry_timestamp=entry_candle.timestamp,
                entry_price=entry_candle.close,
                exit_timestamp=None,
                exit_price=None,
                outcome=TradeOutcome.SKIPPED,
                pnl=0.0,
                reason="insufficient_future_candles",
            )

        exit_candle = candles[expiry_index]
        won = self._is_win(signal.direction, entry_candle.close, exit_candle.close)
        outcome = TradeOutcome.WIN if won else TradeOutcome.LOSS
        pnl = self.stake * self.payout_percentage if won else -self.stake

        logger.info(
            "Simulated trade {} {} entry={} exit={} pnl={}",
            signal.symbol,
            outcome.value,
            entry_candle.close,
            exit_candle.close,
            pnl,
        )

        return BacktestTrade(
            symbol=signal.symbol,
            timeframe=signal.timeframe,
            direction=signal.direction.value,
            strategy_name=signal.strategy_name,
            confidence=signal.confidence,
            entry_timestamp=entry_candle.timestamp,
            entry_price=entry_candle.close,
            exit_timestamp=exit_candle.timestamp,
            exit_price=exit_candle.close,
            outcome=outcome,
            pnl=pnl,
        )

    def _is_win(self, direction: SignalDirection, entry_price: float, exit_price: float) -> bool:
        if direction == SignalDirection.CALL:
            return exit_price > entry_price
        if direction == SignalDirection.PUT:
            return exit_price < entry_price
        return False
