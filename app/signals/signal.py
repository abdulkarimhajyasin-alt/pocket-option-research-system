"""Trade signal domain models."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class SignalDirection(StrEnum):
    """Supported demo signal directions."""

    CALL = "call"
    PUT = "put"


@dataclass(frozen=True)
class TradeSignal:
    """Represents a strategy-generated trade signal for research workflows."""

    symbol: str
    timeframe: str
    direction: SignalDirection
    confidence: float
    timestamp: datetime
    strategy_name: str
