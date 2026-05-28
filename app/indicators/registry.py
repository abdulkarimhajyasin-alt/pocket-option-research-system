"""Indicator registry for dynamic lookup and extension."""

from collections.abc import Callable

from loguru import logger

from app.indicators.base_indicator import BaseIndicator
from app.indicators.momentum import RSI
from app.indicators.trend import EMA, SMA
from app.indicators.volatility import ATR

IndicatorFactory = Callable[..., BaseIndicator]


class IndicatorRegistry:
    """Registry that maps indicator names to factories."""

    def __init__(self) -> None:
        self._factories: dict[str, IndicatorFactory] = {}

    def register(self, name: str, factory: IndicatorFactory) -> None:
        """Register an indicator factory by name."""
        normalized_name = name.strip().lower()
        if not normalized_name:
            raise ValueError("Indicator name is required")
        self._factories[normalized_name] = factory
        logger.info("Registered indicator: {}", normalized_name)

    def get(self, name: str) -> IndicatorFactory:
        """Return an indicator factory by name."""
        normalized_name = name.strip().lower()
        if normalized_name not in self._factories:
            raise KeyError(f"Unknown indicator: {name}")
        return self._factories[normalized_name]

    def create(self, name: str, **parameters: object) -> BaseIndicator:
        """Create an indicator instance by name."""
        logger.info("Creating indicator {} with parameters={}", name, parameters)
        return self.get(name)(**parameters)

    def names(self) -> tuple[str, ...]:
        """Return registered indicator names."""
        return tuple(sorted(self._factories))


def default_indicator_registry() -> IndicatorRegistry:
    """Build the default indicator registry."""
    registry = IndicatorRegistry()
    registry.register("sma", SMA)
    registry.register("ema", EMA)
    registry.register("rsi", RSI)
    registry.register("atr", ATR)
    return registry
