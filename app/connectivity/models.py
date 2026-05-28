"""Connectivity domain models."""

from dataclasses import dataclass, field
from enum import StrEnum


class ConnectorDataMode(StrEnum):
    """Supported read-only connector data modes."""

    LOCAL = "local"
    SIMULATED = "simulated"
    HISTORICAL = "historical"
    LATEST = "latest"


@dataclass(frozen=True)
class ConnectorCapabilities:
    """Read-only connector capabilities."""

    market_data_read: bool = True
    historical_data_read: bool = True
    account_info_read: bool = False
    trade_execution_enabled: bool = False
    supported_symbols: tuple[str, ...] = field(default_factory=tuple)
    supported_timeframes: tuple[str, ...] = field(default_factory=tuple)
    supported_data_modes: tuple[str, ...] = field(default_factory=lambda: ("historical", "latest"))

    def __post_init__(self) -> None:
        """Reject execution-capable connector declarations."""
        if self.trade_execution_enabled:
            raise ValueError("Connector trade execution capability must remain disabled")

    def supports_symbol(self, symbol: str) -> bool:
        """Return True when the connector supports a symbol."""
        return symbol.upper() in {item.upper() for item in self.supported_symbols}

    def supports_timeframe(self, timeframe: str) -> bool:
        """Return True when the connector supports a timeframe."""
        return timeframe.lower() in {item.lower() for item in self.supported_timeframes}

    def to_dict(self) -> dict[str, object]:
        """Return a serializable capabilities payload."""
        return {
            "market_data_read": self.market_data_read,
            "historical_data_read": self.historical_data_read,
            "account_info_read": self.account_info_read,
            "trade_execution_enabled": self.trade_execution_enabled,
            "supported_symbols": list(self.supported_symbols),
            "supported_timeframes": list(self.supported_timeframes),
            "supported_data_modes": list(self.supported_data_modes),
        }
