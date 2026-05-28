"""Connector registry for read-only market-data adapters."""

from collections.abc import Callable

from loguru import logger

from app.connectivity.base_connector import BaseReadOnlyConnector
from app.connectivity.errors import ConnectorValidationError
from app.connectivity.models import ConnectorCapabilities


ConnectorFactory = Callable[[], BaseReadOnlyConnector]


class ConnectorRegistry:
    """Registers and resolves read-only connector factories."""

    def __init__(self) -> None:
        self._factories: dict[str, ConnectorFactory] = {}

    def register(self, name: str, factory: ConnectorFactory) -> None:
        """Register a connector factory."""
        normalized = self._normalize(name)
        if normalized in self._factories:
            raise KeyError(f"Connector already registered: {name}")
        connector = factory()
        self._validate_capabilities(connector.get_capabilities())
        self._factories[normalized] = factory
        logger.bind(component="connectivity").info("Connector registered: {}", normalized)

    def create(self, name: str) -> BaseReadOnlyConnector:
        """Create a connector by name."""
        normalized = self._normalize(name)
        if normalized not in self._factories:
            raise KeyError(f"Unknown connector: {name}")
        connector = self._factories[normalized]()
        self._validate_capabilities(connector.get_capabilities())
        return connector

    def capabilities(self, name: str) -> ConnectorCapabilities:
        """Return capabilities for a connector."""
        return self.create(name).get_capabilities()

    def names(self) -> list[str]:
        """Return registered connector names."""
        return sorted(self._factories)

    def _validate_capabilities(self, capabilities: ConnectorCapabilities) -> None:
        if capabilities.trade_execution_enabled:
            raise ConnectorValidationError("Execution-capable connectors are forbidden")

    def _normalize(self, name: str) -> str:
        return name.strip().lower()
