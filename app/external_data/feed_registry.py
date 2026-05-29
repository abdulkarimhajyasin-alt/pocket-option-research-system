"""Registry for broker-agnostic read-only external feeds."""

from collections.abc import Callable

from app.external_data.base_feed import BaseExternalFeed, FeedContract
from app.external_data.feed_errors import FeedRegistryError

FeedFactory = Callable[[], BaseExternalFeed]


class ExternalFeedRegistry:
    """Register and create external feeds without execution capabilities."""

    def __init__(self) -> None:
        self._factories: dict[str, FeedFactory] = {}
        self._contracts: dict[str, FeedContract] = {}

    def register(self, name: str, factory: FeedFactory, contract: FeedContract) -> None:
        """Register a read-only feed factory."""
        key = name.strip().lower()
        if not key:
            raise FeedRegistryError("Feed name is required")
        contract.validate()
        self._factories[key] = factory
        self._contracts[key] = contract

    def create(self, name: str) -> BaseExternalFeed:
        """Create a registered feed."""
        key = name.strip().lower()
        if key not in self._factories:
            raise FeedRegistryError(f"Unknown external feed: {name}")
        feed = self._factories[key]()
        forbidden = ("place_trade", "execute_trade", "submit_order", "login")
        if any(hasattr(feed, attr) for attr in forbidden):
            raise FeedRegistryError("External feed exposes forbidden execution capability")
        return feed

    def names(self) -> tuple[str, ...]:
        """Return registered feed names."""
        return tuple(sorted(self._factories))

    def contract(self, name: str) -> FeedContract:
        """Return registered feed contract metadata."""
        key = name.strip().lower()
        if key not in self._contracts:
            raise FeedRegistryError(f"Unknown external feed: {name}")
        return self._contracts[key]
