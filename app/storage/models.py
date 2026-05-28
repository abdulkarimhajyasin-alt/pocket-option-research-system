"""Storage domain models for durable local persistence."""

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


def utc_now() -> datetime:
    """Return the current UTC timestamp."""
    return datetime.now(tz=UTC)


@dataclass(frozen=True)
class StoredEvent:
    """Append-only event store record."""

    event_type: str
    aggregate_id: str
    payload: dict[str, Any]
    timestamp: datetime = field(default_factory=utc_now)
    session_id: str = "default"
    event_id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable event dictionary."""
        row = asdict(self)
        row["timestamp"] = self.timestamp.isoformat()
        return row


@dataclass(frozen=True)
class StoredTrade:
    """Persisted trade lifecycle record."""

    trade_id: str
    strategy_name: str
    symbol: str
    timeframe: str
    direction: str
    lifecycle_state: str
    timestamp: datetime
    confidence: float = 0.0
    pnl: float = 0.0
    outcome: str | None = None
    rejection_reason: str | None = None
    session_id: str = "default"


@dataclass(frozen=True)
class StoredSignal:
    """Persisted signal record."""

    signal_id: str
    strategy_name: str
    symbol: str
    timeframe: str
    direction: str
    confidence: float
    timestamp: datetime
    session_id: str = "default"


@dataclass(frozen=True)
class StoredRuntimeEvent:
    """Persisted runtime event."""

    event_id: str
    event_type: str
    timestamp: datetime
    message: str
    payload: dict[str, Any] = field(default_factory=dict)
    session_id: str = "default"


@dataclass(frozen=True)
class StoredRiskEvent:
    """Persisted risk validation event."""

    event_id: str
    timestamp: datetime
    strategy_name: str
    symbol: str
    timeframe: str
    approved: bool
    reason: str | None
    message: str
    state_snapshot: dict[str, Any]
    session_id: str = "default"


@dataclass(frozen=True)
class StoredAnalyticsSnapshot:
    """Persisted analytics snapshot."""

    snapshot_id: str
    timestamp: datetime
    snapshot_type: str
    payload: dict[str, Any]
    session_id: str = "default"


@dataclass(frozen=True)
class StoredRuntimeState:
    """Persisted runtime state snapshot."""

    state_id: str
    timestamp: datetime
    mode: str
    active: bool
    health: str
    payload: dict[str, Any]
    session_id: str = "default"


@dataclass(frozen=True)
class StoredBrokerHealthEvent:
    """Persisted broker health snapshot."""

    event_id: str
    timestamp: datetime
    broker_name: str
    status: str
    connected: bool
    payload: dict[str, Any]
    session_id: str = "default"


@dataclass(frozen=True)
class StoredExecutionEvent:
    """Persisted execution lifecycle event."""

    event_id: str
    timestamp: datetime
    trade_id: str
    lifecycle_state: str
    payload: dict[str, Any]
    session_id: str = "default"
