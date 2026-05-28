"""Broker runtime lifecycle integration."""

from dataclasses import dataclass

from loguru import logger

from app.brokers.base_broker import BaseBroker
from app.brokers.health import BrokerHealthSnapshot


@dataclass(frozen=True)
class BrokerRuntimeDiagnostics:
    """Broker runtime diagnostic snapshot."""

    connected: bool
    health: dict[str, object]
    capabilities: dict[str, object]


class BrokerRuntime:
    """Coordinates broker initialization, heartbeat, and safe shutdown."""

    def __init__(self, broker: BaseBroker) -> None:
        self.broker = broker

    def initialize(self) -> None:
        """Validate and connect a broker adapter."""
        logger.bind(component="broker").info("Initializing broker runtime")
        self.broker.validate_environment()
        self.broker.connect()

    def heartbeat(self) -> BrokerHealthSnapshot:
        """Run broker heartbeat and return health."""
        self.broker.ping()
        health = self.broker.get_status().health
        logger.bind(component="broker").info("Broker heartbeat health={}", health.to_dict())
        return health

    def shutdown(self) -> None:
        """Disconnect broker adapter safely."""
        logger.bind(component="broker").info("Broker runtime shutdown")
        self.broker.disconnect()

    def diagnostics(self) -> BrokerRuntimeDiagnostics:
        """Return runtime diagnostics for a broker adapter."""
        status = self.broker.get_status()
        return BrokerRuntimeDiagnostics(
            connected=status.connected,
            health=status.health.to_dict(),
            capabilities=self.broker.get_capabilities().to_dict(),
        )
