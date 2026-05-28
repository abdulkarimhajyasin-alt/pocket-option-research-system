"""Configuration validation helpers."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ConfigValidationIssue:
    """Represents a configuration warning or failure."""

    message: str
    critical: bool = False


@dataclass
class ConfigValidationResult:
    """Structured configuration validation result."""

    issues: list[ConfigValidationIssue] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """Return True when no critical issues exist."""
        return not any(issue.critical for issue in self.issues)

    @property
    def warnings(self) -> list[str]:
        """Return non-critical validation messages."""
        return [issue.message for issue in self.issues if not issue.critical]

    @property
    def failures(self) -> list[str]:
        """Return critical validation messages."""
        return [issue.message for issue in self.issues if issue.critical]

    def add(self, message: str, critical: bool = False) -> None:
        """Add a validation issue."""
        self.issues.append(ConfigValidationIssue(message=message, critical=critical))


class ConfigValidator:
    """Validates resolved application configuration."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)

    def validate(self, config: dict[str, Any]) -> ConfigValidationResult:
        """Validate key operational configuration sections."""
        result = ConfigValidationResult()
        for section in (
            "environment",
            "runtime",
            "strategy",
            "risk",
            "broker",
            "storage",
            "connectivity",
        ):
            if section not in config:
                result.add(f"Missing config section: {section}", critical=True)
        broker = config.get("broker", {})
        mode = str(broker.get("mode", "demo")).lower()
        if mode == "live":
            result.add("Live broker mode is not allowed in this platform phase", critical=True)
        connectivity = config.get("connectivity", {})
        if not bool(connectivity.get("read_only", True)):
            result.add("Connectivity configuration must be read-only", critical=True)
        if bool(connectivity.get("execution_enabled", False)):
            result.add("Connectivity execution must remain disabled", critical=True)
        runtime = config.get("runtime", {})
        data_path = runtime.get("data_path")
        if data_path and not (self.project_root / str(data_path)).exists():
            result.add(f"Runtime data file not found: {data_path}", critical=True)
        return result
