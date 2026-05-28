"""Connector health tracking models."""

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum


class ConnectorHealthStatus(StrEnum):
    """Connector health states."""

    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    DEGRADED = "degraded"
    FAILED = "failed"


@dataclass
class ConnectorHealthSnapshot:
    """Health snapshot for a read-only connector."""

    status: ConnectorHealthStatus = ConnectorHealthStatus.DISCONNECTED
    connected: bool = False
    latency_ms: float = 0.0
    last_heartbeat: datetime | None = None
    error_count: int = 0
    reconnect_attempts: int = 0
    last_data_timestamp: datetime | None = None

    def mark_connected(self, latency_ms: float = 0.0) -> None:
        """Mark connector as connected."""
        self.status = ConnectorHealthStatus.CONNECTED
        self.connected = True
        self.latency_ms = round(latency_ms, 4)
        self.last_heartbeat = datetime.now(tz=UTC)

    def mark_disconnected(self) -> None:
        """Mark connector as disconnected."""
        self.status = ConnectorHealthStatus.DISCONNECTED
        self.connected = False

    def mark_error(self) -> None:
        """Record a connector error."""
        self.error_count += 1
        self.status = (
            ConnectorHealthStatus.DEGRADED
            if self.connected
            else ConnectorHealthStatus.FAILED
        )

    def to_dict(self) -> dict[str, object]:
        """Return a serializable health payload."""
        return {
            "status": self.status.value,
            "connected": self.connected,
            "latency_ms": self.latency_ms,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "error_count": self.error_count,
            "reconnect_attempts": self.reconnect_attempts,
            "last_data_timestamp": (
                self.last_data_timestamp.isoformat() if self.last_data_timestamp else None
            ),
        }
