"""Exposure tracking for active simulated trades."""

from dataclasses import dataclass
from datetime import datetime

from app.signals.signal import TradeSignal


@dataclass(frozen=True)
class ActiveTrade:
    """Represents an active trade for exposure accounting."""

    trade_id: str
    symbol: str
    strategy_name: str
    direction: str
    opened_at: datetime


class ExposureTracker:
    """Tracks active exposure by symbol, strategy, and direction."""

    def __init__(self) -> None:
        self._active_trades: dict[str, ActiveTrade] = {}

    def register(self, trade_id: str, signal: TradeSignal) -> None:
        """Register an active trade from an approved signal."""
        self._active_trades[trade_id] = ActiveTrade(
            trade_id=trade_id,
            symbol=signal.symbol,
            strategy_name=signal.strategy_name,
            direction=signal.direction.value,
            opened_at=signal.timestamp,
        )

    def close(self, trade_id: str) -> None:
        """Remove a trade from active exposure."""
        self._active_trades.pop(trade_id, None)

    def total_active(self) -> int:
        """Return the number of active trades."""
        return len(self._active_trades)

    def symbol_exposure(self, symbol: str) -> int:
        """Return active exposure count for one symbol."""
        return sum(1 for trade in self._active_trades.values() if trade.symbol == symbol)

    def strategy_exposure(self, strategy_name: str) -> int:
        """Return active exposure count for one strategy."""
        return sum(
            1 for trade in self._active_trades.values() if trade.strategy_name == strategy_name
        )

    def direction_exposure(self, direction: str) -> int:
        """Return active exposure count for one direction."""
        return sum(1 for trade in self._active_trades.values() if trade.direction == direction)

    def snapshot(self) -> dict[str, int]:
        """Return exposure metrics prepared for portfolio-level controls."""
        symbols = {trade.symbol for trade in self._active_trades.values()}
        strategies = {trade.strategy_name for trade in self._active_trades.values()}
        directions = {trade.direction for trade in self._active_trades.values()}
        return {
            "active_trades": self.total_active(),
            **{f"symbol:{symbol}": self.symbol_exposure(symbol) for symbol in sorted(symbols)},
            **{
                f"strategy:{strategy}": self.strategy_exposure(strategy)
                for strategy in sorted(strategies)
            },
            **{
                f"direction:{direction}": self.direction_exposure(direction)
                for direction in sorted(directions)
            },
        }
