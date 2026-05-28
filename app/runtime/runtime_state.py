"""Runtime state models for local paper trading sessions."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum


class RuntimeMode(StrEnum):
    """Supported runtime modes."""

    PAPER = "paper"
    SAFE = "safe"


class RuntimeHealth(StrEnum):
    """Runtime health states."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    STOPPED = "stopped"


@dataclass
class RuntimeMetrics:
    """Mutable runtime counters."""

    processed_candles: int = 0
    generated_signals: int = 0
    executed_trades: int = 0
    blocked_trades: int = 0
    settled_trades: int = 0
    runtime_errors: int = 0


@dataclass
class RuntimeState:
    """Tracks runtime lifecycle state."""

    mode: RuntimeMode
    active: bool = False
    health: RuntimeHealth = RuntimeHealth.STOPPED
    start_time: datetime | None = None
    stop_time: datetime | None = None
    emergency_stop: bool = False
    metrics: RuntimeMetrics = field(default_factory=RuntimeMetrics)

    def start(self) -> None:
        """Mark runtime as active."""
        self.active = True
        self.health = RuntimeHealth.HEALTHY
        self.start_time = datetime.now(tz=UTC)
        self.stop_time = None

    def stop(self) -> None:
        """Mark runtime as stopped."""
        self.active = False
        self.health = RuntimeHealth.STOPPED
        self.stop_time = datetime.now(tz=UTC)

    @property
    def uptime_seconds(self) -> float:
        """Return runtime uptime in seconds."""
        if self.start_time is None:
            return 0.0
        end = self.stop_time or datetime.now(tz=UTC)
        return max(0.0, (end - self.start_time).total_seconds())

    def snapshot(self) -> dict[str, object]:
        """Return a serializable runtime state snapshot."""
        return {
            "mode": self.mode.value,
            "active": self.active,
            "health": self.health.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "stop_time": self.stop_time.isoformat() if self.stop_time else None,
            "uptime_seconds": round(self.uptime_seconds, 4),
            "emergency_stop": self.emergency_stop,
            "metrics": self.metrics.__dict__.copy(),
        }
