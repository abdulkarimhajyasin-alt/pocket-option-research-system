"""Broker interface definitions."""

from abc import ABC, abstractmethod
from typing import Any

from app.signals.signal import TradeSignal


class BaseBroker(ABC):
    """Abstract broker interface for demo and future execution adapters."""

    @abstractmethod
    def connect(self) -> None:
        """Connect to the broker adapter."""

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the broker adapter."""

    @abstractmethod
    def get_balance(self) -> float:
        """Return the current account balance."""

    @abstractmethod
    def place_trade(self, signal: TradeSignal) -> dict[str, Any]:
        """Place a trade using a validated signal."""
