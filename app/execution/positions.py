"""Position tracking for local paper execution."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class PositionStatus(StrEnum):
    """Paper position lifecycle states."""

    OPEN = "open"
    CLOSED = "closed"


@dataclass(frozen=True)
class Position:
    """Represents a paper trading position."""

    trade_id: str
    symbol: str
    timeframe: str
    direction: str
    strategy_name: str
    entry_price: float
    stake: float
    opened_at: datetime
    expiry_timestamp: datetime
    status: PositionStatus = PositionStatus.OPEN
    exit_price: float | None = None
    pnl: float = 0.0
    closed_at: datetime | None = None


class PositionTracker:
    """Tracks open and closed paper positions."""

    def __init__(self) -> None:
        self.open_positions: dict[str, Position] = {}
        self.closed_positions: dict[str, Position] = {}

    def open(self, position: Position) -> None:
        """Track a newly opened position."""
        self.open_positions[position.trade_id] = position

    def close(
        self,
        trade_id: str,
        exit_price: float,
        pnl: float,
        closed_at: datetime,
    ) -> Position:
        """Close an open position and return the closed record."""
        position = self.open_positions.pop(trade_id)
        closed = Position(
            trade_id=position.trade_id,
            symbol=position.symbol,
            timeframe=position.timeframe,
            direction=position.direction,
            strategy_name=position.strategy_name,
            entry_price=position.entry_price,
            stake=position.stake,
            opened_at=position.opened_at,
            expiry_timestamp=position.expiry_timestamp,
            status=PositionStatus.CLOSED,
            exit_price=exit_price,
            pnl=pnl,
            closed_at=closed_at,
        )
        self.closed_positions[trade_id] = closed
        return closed

    def get_open_positions(self) -> list[Position]:
        """Return open positions."""
        return list(self.open_positions.values())

    def get_closed_positions(self) -> list[Position]:
        """Return closed positions."""
        return list(self.closed_positions.values())

    def symbol_exposure(self, symbol: str) -> int:
        """Return open position count for a symbol."""
        return sum(1 for position in self.open_positions.values() if position.symbol == symbol)
