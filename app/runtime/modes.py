"""Operational runtime modes and safety restrictions."""

from dataclasses import dataclass
from enum import StrEnum


class OperationalMode(StrEnum):
    """Supported high-level application modes."""

    BACKTEST = "backtest"
    PAPER = "paper"
    RESEARCH = "research"
    DEBUG = "debug"


@dataclass(frozen=True)
class ModeValidationResult:
    """Result of validating an operational mode."""

    mode: OperationalMode
    allowed: bool
    reason: str = ""


class ModePolicy:
    """Enforces safe operational mode restrictions."""

    _allowed_modes = {
        OperationalMode.BACKTEST,
        OperationalMode.PAPER,
        OperationalMode.RESEARCH,
        OperationalMode.DEBUG,
    }

    def validate(self, mode: str | OperationalMode) -> ModeValidationResult:
        """Validate that a mode is supported and local-safe."""
        try:
            operational_mode = OperationalMode(str(mode))
        except ValueError:
            return ModeValidationResult(
                mode=OperationalMode.DEBUG,
                allowed=False,
                reason=f"Unsupported operational mode: {mode}",
            )
        if operational_mode not in self._allowed_modes:
            return ModeValidationResult(operational_mode, False, "Mode is not allowed")
        return ModeValidationResult(operational_mode, True)
