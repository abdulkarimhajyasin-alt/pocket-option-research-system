"""Strategy base abstractions."""

from abc import ABC, abstractmethod
from typing import Any

from app.signals.signal import TradeSignal


class BaseStrategy(ABC):
    """Abstract base class for all experimental trading strategies."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the stable strategy name."""

    @abstractmethod
    def generate_signal(self, market_data: Any) -> TradeSignal | None:
        """Generate a trade signal from market data, or return None."""
