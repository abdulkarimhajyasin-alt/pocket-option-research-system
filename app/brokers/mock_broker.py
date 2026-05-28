"""Mock broker implementation for demo-only execution."""

from typing import Any
from uuid import uuid4

from loguru import logger

from app.brokers.base_broker import BaseBroker
from app.signals.signal import TradeSignal


class MockBroker(BaseBroker):
    """Simulates broker behavior without connecting to any external service."""

    def __init__(self, initial_balance: float = 10_000.0) -> None:
        self._balance = initial_balance
        self._connected = False

    def connect(self) -> None:
        """Simulate a broker connection."""
        self._connected = True
        logger.info("Mock broker connected")

    def disconnect(self) -> None:
        """Simulate a broker disconnection."""
        self._connected = False
        logger.info("Mock broker disconnected")

    def get_balance(self) -> float:
        """Return the simulated account balance."""
        return self._balance

    def place_trade(self, signal: TradeSignal) -> dict[str, Any]:
        """Simulate trade execution for a validated signal."""
        if not self._connected:
            raise RuntimeError("Mock broker is not connected")

        trade = {
            "trade_id": str(uuid4()),
            "symbol": signal.symbol,
            "timeframe": signal.timeframe,
            "direction": signal.direction.value,
            "status": "simulated",
            "balance": self._balance,
        }
        logger.info("Mock trade simulated: {}", trade)
        return trade
