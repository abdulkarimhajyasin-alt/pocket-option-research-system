"""Broker capability models."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class BrokerCapabilities:
    """Declares what a broker adapter can safely support."""

    demo_supported: bool = True
    live_supported: bool = False
    supported_symbols: tuple[str, ...] = field(default_factory=tuple)
    supported_timeframes: tuple[str, ...] = field(default_factory=tuple)
    payout_supported: bool = True
    trade_types: tuple[str, ...] = ("binary_option",)
    historical_data_supported: bool = False

    def supports_symbol(self, symbol: str) -> bool:
        """Return True if the symbol is supported."""
        return symbol.upper() in {item.upper() for item in self.supported_symbols}

    def supports_timeframe(self, timeframe: str) -> bool:
        """Return True if the timeframe is supported."""
        return timeframe.lower() in {item.lower() for item in self.supported_timeframes}

    def to_dict(self) -> dict[str, bool | list[str]]:
        """Return a serializable capability snapshot."""
        return {
            "demo_supported": self.demo_supported,
            "live_supported": self.live_supported,
            "supported_symbols": list(self.supported_symbols),
            "supported_timeframes": list(self.supported_timeframes),
            "payout_supported": self.payout_supported,
            "trade_types": list(self.trade_types),
            "historical_data_supported": self.historical_data_supported,
        }
