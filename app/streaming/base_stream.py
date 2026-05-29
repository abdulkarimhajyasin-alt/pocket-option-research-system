"""Broker-agnostic base interface for read-only market streams."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.streaming.health import StreamHealthSnapshot
from app.streaming.models import MarketDataEvent


class BaseMarketStream(ABC):
    """Abstract read-only market data stream.

    Streams expose market data only. They intentionally have no trade placement,
    credential handling, broker automation, or execution-oriented methods.
    """

    source: str

    @abstractmethod
    def start(self) -> None:
        """Start local stream processing."""

    @abstractmethod
    def stop(self) -> None:
        """Stop local stream processing and release resources."""

    @abstractmethod
    def is_running(self) -> bool:
        """Return True when the stream is running."""

    @abstractmethod
    def get_health(self) -> StreamHealthSnapshot:
        """Return stream health diagnostics."""

    @abstractmethod
    def subscribe(self, symbol: str, timeframe: str) -> None:
        """Subscribe to a read-only symbol/timeframe data flow."""

    @abstractmethod
    def unsubscribe(self, symbol: str, timeframe: str) -> None:
        """Remove a read-only symbol/timeframe subscription."""

    @abstractmethod
    def next_event(self) -> MarketDataEvent | None:
        """Return the next available market event, if any."""

    @abstractmethod
    def validate_environment(self) -> None:
        """Validate local-only stream prerequisites."""
