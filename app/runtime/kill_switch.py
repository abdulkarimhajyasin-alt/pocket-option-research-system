"""Runtime kill switch controls."""

from dataclasses import dataclass

from loguru import logger

from app.runtime.health import HealthReport
from app.runtime.runtime_state import RuntimeHealth, RuntimeState


@dataclass(frozen=True)
class KillSwitchConfig:
    """Configurable runtime stop conditions."""

    stop_on_health_failure: bool = True
    max_runtime_errors: int = 5
    stop_on_risk_shutdown: bool = True


class KillSwitch:
    """Evaluates manual and automatic runtime stop conditions."""

    def __init__(self, config: KillSwitchConfig | None = None) -> None:
        self.config = config or KillSwitchConfig()
        self.manual_stop_requested = False
        self.reason: str | None = None

    def emergency_stop(self, reason: str) -> None:
        """Activate a manual emergency stop."""
        self.manual_stop_requested = True
        self.reason = reason
        logger.critical("Kill switch activated: {}", reason)

    def should_stop(
        self,
        state: RuntimeState,
        health_report: HealthReport,
        risk_shutdown_events: list[str] | None = None,
    ) -> bool:
        """Return True when runtime should stop."""
        if self.manual_stop_requested:
            return True
        if (
            self.config.stop_on_health_failure
            and health_report.status == RuntimeHealth.FAILED
        ):
            self.reason = "runtime_health_failed"
            logger.critical("Kill switch activated by health failure")
            return True
        if state.metrics.runtime_errors >= self.config.max_runtime_errors:
            self.reason = "runtime_error_limit"
            logger.critical("Kill switch activated by runtime error limit")
            return True
        if self.config.stop_on_risk_shutdown and risk_shutdown_events:
            self.reason = "risk_shutdown"
            logger.critical("Kill switch activated by risk shutdown event")
            return True
        return False
