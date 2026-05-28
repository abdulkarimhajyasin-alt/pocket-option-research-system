"""Broker domain models."""

from dataclasses import dataclass
from enum import StrEnum

from app.brokers.health import BrokerHealthSnapshot


class BrokerMode(StrEnum):
    """Supported broker adapter modes."""

    DEMO = "demo"
    LIVE = "live"


@dataclass(frozen=True)
class BrokerStatus:
    """Runtime broker status returned by adapters."""

    name: str
    mode: BrokerMode
    connected: bool
    health: BrokerHealthSnapshot

    def to_dict(self) -> dict[str, object]:
        """Return a serializable status snapshot."""
        return {
            "name": self.name,
            "mode": self.mode.value,
            "connected": self.connected,
            "health": self.health.to_dict(),
        }
