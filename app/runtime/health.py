"""Runtime health monitoring."""

from dataclasses import dataclass, field
from datetime import UTC, datetime

from loguru import logger

from app.runtime.runtime_state import RuntimeHealth


@dataclass
class HealthReport:
    """Structured health report."""

    status: RuntimeHealth
    heartbeat: datetime
    component_failures: dict[str, int] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def snapshot(self) -> dict[str, object]:
        """Return report as serializable data."""
        return {
            "status": self.status.value,
            "heartbeat": self.heartbeat.isoformat(),
            "component_failures": dict(self.component_failures),
            "warnings": list(self.warnings),
        }


class HealthMonitor:
    """Tracks component and runtime health."""

    def __init__(self, max_failures: int = 3) -> None:
        self.max_failures = max_failures
        self.component_failures: dict[str, int] = {}
        self.warnings: list[str] = []
        self.last_heartbeat = datetime.now(tz=UTC)

    def heartbeat(self) -> None:
        """Refresh runtime heartbeat."""
        self.last_heartbeat = datetime.now(tz=UTC)

    def record_failure(self, component: str, message: str) -> None:
        """Record a component failure."""
        self.component_failures[component] = self.component_failures.get(component, 0) + 1
        warning = f"{component}: {message}"
        self.warnings.append(warning)
        logger.warning("Runtime health warning: {}", warning)

    def report(self) -> HealthReport:
        """Return current health status."""
        status = RuntimeHealth.HEALTHY
        if any(count >= self.max_failures for count in self.component_failures.values()):
            status = RuntimeHealth.FAILED
        elif self.component_failures:
            status = RuntimeHealth.DEGRADED
        return HealthReport(status, self.last_heartbeat, self.component_failures, self.warnings)
