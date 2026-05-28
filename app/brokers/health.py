"""Broker health state models."""

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum


class BrokerHealthStatus(StrEnum):
    """Broker adapter health states."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DEGRADED = "degraded"
    FAILED = "failed"


@dataclass(frozen=True)
class BrokerHealthSnapshot:
    """Structured broker health snapshot."""

    status: BrokerHealthStatus
    connected: bool
    last_heartbeat: datetime | None
    response_latency_ms: float
    error_count: int
    reconnect_attempts: int

    def to_dict(self) -> dict[str, str | bool | float | int | None]:
        """Return a serializable health snapshot."""
        return {
            "status": self.status.value,
            "connected": self.connected,
            "last_heartbeat": self.last_heartbeat.isoformat()
            if self.last_heartbeat
            else None,
            "response_latency_ms": round(self.response_latency_ms, 4),
            "error_count": self.error_count,
            "reconnect_attempts": self.reconnect_attempts,
        }


def utc_now() -> datetime:
    """Return the current UTC timestamp."""
    return datetime.now(tz=UTC)
