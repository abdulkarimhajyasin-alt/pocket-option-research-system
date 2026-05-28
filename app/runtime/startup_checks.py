"""Startup validation checks for orchestrated runtime sessions."""

from dataclasses import dataclass, field
from pathlib import Path

from app.config.config_manager import AppConfig
from app.runtime.modes import ModePolicy


@dataclass(frozen=True)
class StartupCheck:
    """Single startup validation check result."""

    name: str
    passed: bool
    message: str
    critical: bool = False


@dataclass
class StartupValidationResult:
    """Structured startup validation result."""

    checks: list[StartupCheck] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """Return True when no critical startup checks failed."""
        return not any(not check.passed and check.critical for check in self.checks)

    @property
    def warnings(self) -> list[str]:
        """Return failed non-critical checks."""
        return [check.message for check in self.checks if not check.passed and not check.critical]

    @property
    def failures(self) -> list[str]:
        """Return failed critical checks."""
        return [check.message for check in self.checks if not check.passed and check.critical]

    def add(self, name: str, passed: bool, message: str, critical: bool = False) -> None:
        """Add a check result."""
        self.checks.append(StartupCheck(name, passed, message, critical))


class StartupValidator:
    """Runs startup checks before runtime orchestration."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.mode_policy = ModePolicy()

    def validate(self, config: AppConfig) -> StartupValidationResult:
        """Validate config, directories, storage, broker safety, and mode."""
        result = StartupValidationResult()
        result.add(
            "config",
            config.validation.passed,
            (
                "Resolved configuration is valid"
                if config.validation.passed
                else "; ".join(config.validation.failures)
            ),
            critical=True,
        )
        for directory in ("logs", "reports", "storage"):
            path = self.project_root / directory
            path.mkdir(parents=True, exist_ok=True)
            result.add(
                f"directory:{directory}",
                path.exists(),
                f"Directory available: {directory}",
                critical=True,
            )
        storage_path = self.project_root / str(
            config.get("storage.database_path", "storage/trading_system.db")
        )
        result.add(
            "database_path",
            storage_path.parent.exists(),
            f"Database directory available: {storage_path.parent}",
            critical=True,
        )
        broker_mode = str(config.get("broker.mode", "demo")).lower()
        live_supported = bool(config.get("broker.capabilities.live_supported", False))
        broker_safe = broker_mode != "live" and not live_supported
        result.add(
            "broker_safety",
            broker_safe,
            "Broker configuration is demo-only",
            critical=True,
        )
        mode_result = self.mode_policy.validate(config.environment.mode)
        result.add(
            "operational_mode",
            mode_result.allowed,
            mode_result.reason or f"Operational mode allowed: {mode_result.mode.value}",
            critical=True,
        )
        strategy_name = str(config.get("strategy.name", "")).strip()
        result.add(
            "strategy",
            bool(strategy_name),
            f"Strategy configured: {strategy_name}",
            critical=True,
        )
        read_only = bool(config.get("connectivity.read_only", True))
        execution_enabled = bool(config.get("connectivity.execution_enabled", False))
        result.add(
            "connectivity_safety",
            read_only and not execution_enabled,
            "Connectivity configuration is read-only",
            critical=True,
        )
        connectors = config.get("connectivity.connectors", {})
        result.add(
            "connectivity_configs",
            isinstance(connectors, dict) and bool(connectors),
            "Connectivity connector configs available",
            critical=False,
        )
        return result
