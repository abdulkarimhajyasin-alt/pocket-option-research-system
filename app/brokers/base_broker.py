"""Broker interface definitions."""

from abc import ABC, abstractmethod
from typing import Any

from app.brokers.capabilities import BrokerCapabilities
from app.brokers.health import BrokerHealthSnapshot, BrokerHealthStatus
from app.brokers.models import BrokerMode, BrokerStatus
from app.signals.signal import TradeSignal


class BaseBroker(ABC):
    """Abstract broker interface for demo and future execution adapters."""

    name = "base_broker"
    mode = BrokerMode.DEMO

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

    def ping(self) -> bool:
        """Return True when the broker adapter is reachable."""
        return self.get_status().connected

    def get_status(self) -> BrokerStatus:
        """Return broker runtime status."""
        connected = bool(getattr(self, "_connected", False))
        status = BrokerHealthStatus.CONNECTED if connected else BrokerHealthStatus.DISCONNECTED
        return BrokerStatus(
            name=self.name,
            mode=self.mode,
            connected=connected,
            health=BrokerHealthSnapshot(
                status=status,
                connected=connected,
                last_heartbeat=None,
                response_latency_ms=0.0,
                error_count=0,
                reconnect_attempts=0,
            ),
        )

    def get_capabilities(self) -> BrokerCapabilities:
        """Return broker capabilities."""
        return BrokerCapabilities(
            demo_supported=True,
            live_supported=False,
            supported_symbols=("EURUSD",),
            supported_timeframes=("1m",),
        )

    def validate_environment(self) -> bool:
        """Validate broker environment before runtime use."""
        capabilities = self.get_capabilities()
        if self.mode == BrokerMode.LIVE or capabilities.live_supported:
            return False
        return capabilities.demo_supported

    def supports_symbol(self, symbol: str) -> bool:
        """Return True if this broker supports a symbol."""
        return self.get_capabilities().supports_symbol(symbol)

    def supports_timeframe(self, timeframe: str) -> bool:
        """Return True if this broker supports a timeframe."""
        return self.get_capabilities().supports_timeframe(timeframe)
