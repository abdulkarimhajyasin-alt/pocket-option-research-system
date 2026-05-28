"""Local paper trading broker adapter."""

from datetime import timedelta
from typing import Any
from uuid import uuid4

from loguru import logger

from app.backtesting.models import TradeOutcome
from app.brokers.base_broker import BaseBroker
from app.data.models import Candle
from app.execution.positions import Position, PositionTracker
from app.signals.signal import SignalDirection, TradeSignal


class PaperBroker(BaseBroker):
    """Simulates account balance, positions, and binary-option settlements locally."""

    def __init__(
        self,
        initial_balance: float = 10_000.0,
        payout_percentage: float = 0.80,
        stake: float = 1.0,
        expiry_candles: int = 1,
    ) -> None:
        self._balance = initial_balance
        self.payout_percentage = payout_percentage
        self.stake = stake
        self.expiry_candles = expiry_candles
        self._connected = False
        self.positions = PositionTracker()
        self.trade_history: list[dict[str, Any]] = []

    def connect(self) -> None:
        """Start the local paper broker."""
        self._connected = True
        logger.info("Paper broker connected balance={}", self._balance)

    def disconnect(self) -> None:
        """Stop the local paper broker."""
        self._connected = False
        logger.info("Paper broker disconnected")

    def get_balance(self) -> float:
        """Return simulated account balance."""
        return self._balance

    def place_trade(self, signal: TradeSignal, candle: Candle | None = None) -> dict[str, Any]:
        """Open a simulated position from a validated signal."""
        if not self._connected:
            raise RuntimeError("Paper broker is not connected")
        if candle is None:
            raise ValueError("Paper broker requires candle context for local execution")

        trade_id = str(uuid4())
        expiry_timestamp = candle.timestamp + timedelta(minutes=self.expiry_candles)
        position = Position(
            trade_id=trade_id,
            symbol=signal.symbol,
            timeframe=signal.timeframe,
            direction=signal.direction.value,
            strategy_name=signal.strategy_name,
            entry_price=candle.close,
            stake=self.stake,
            opened_at=candle.timestamp,
            expiry_timestamp=expiry_timestamp,
        )
        self.positions.open(position)
        event = {
            "trade_id": trade_id,
            "status": "executed",
            "symbol": signal.symbol,
            "direction": signal.direction.value,
            "entry_price": candle.close,
            "stake": self.stake,
            "expiry_timestamp": expiry_timestamp.isoformat(),
        }
        self.trade_history.append(event)
        logger.info("Paper trade opened: {}", event)
        return event

    def settle_trade(self, trade_id: str, candle: Candle) -> dict[str, Any]:
        """Settle an open paper trade using the provided candle close."""
        position = self.positions.open_positions[trade_id]
        won = self._is_win(position.direction, position.entry_price, candle.close)
        pnl = self.stake * self.payout_percentage if won else -self.stake
        self._balance += pnl
        closed = self.positions.close(trade_id, candle.close, pnl, candle.timestamp)
        outcome = TradeOutcome.WIN if won else TradeOutcome.LOSS
        event = {
            "trade_id": trade_id,
            "status": "settled",
            "outcome": outcome.value,
            "entry_price": closed.entry_price,
            "exit_price": candle.close,
            "pnl": pnl,
            "balance": self._balance,
            "settled_at": candle.timestamp.isoformat(),
        }
        self.trade_history.append(event)
        logger.info("Paper trade settled: {}", event)
        return event

    def get_open_positions(self) -> list[Position]:
        """Return open paper positions."""
        return self.positions.get_open_positions()

    def get_trade_history(self) -> list[dict[str, Any]]:
        """Return paper trade lifecycle history."""
        return list(self.trade_history)

    def _is_win(self, direction: str, entry_price: float, exit_price: float) -> bool:
        if direction == SignalDirection.CALL.value:
            return exit_price > entry_price
        if direction == SignalDirection.PUT.value:
            return exit_price < entry_price
        return False
