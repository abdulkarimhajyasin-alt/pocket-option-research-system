"""Broker adapter registry."""

from collections.abc import Callable

from loguru import logger

from app.brokers.base_broker import BaseBroker
from app.brokers.capabilities import BrokerCapabilities


BrokerFactory = Callable[[], BaseBroker]


class BrokerRegistry:
    """Registers and resolves broker adapters by name."""

    def __init__(self) -> None:
        self._factories: dict[str, BrokerFactory] = {}

    def register(self, name: str, factory: BrokerFactory) -> None:
        """Register a broker factory."""
        normalized = self._normalize(name)
        if normalized in self._factories:
            raise KeyError(f"Broker already registered: {name}")
        self._factories[normalized] = factory
        logger.bind(component="broker").info("Broker registered: {}", normalized)

    def create(self, name: str) -> BaseBroker:
        """Create a broker adapter by name."""
        normalized = self._normalize(name)
        if normalized not in self._factories:
            raise KeyError(f"Unknown broker: {name}")
        broker = self._factories[normalized]()
        logger.bind(component="broker").info("Broker created: {}", normalized)
        return broker

    def capabilities(self, name: str) -> BrokerCapabilities:
        """Return capabilities for a registered broker."""
        broker = self.create(name)
        return broker.get_capabilities()

    def names(self) -> list[str]:
        """Return registered broker names."""
        return sorted(self._factories)

    def _normalize(self, name: str) -> str:
        return name.strip().lower()
