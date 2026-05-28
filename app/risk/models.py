"""Risk management domain models."""

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class RiskRejectionReason(StrEnum):
    """Structured reasons a signal can be rejected by risk controls."""

    MAX_TRADES_PER_DAY = "max_trades_per_day"
    MAX_CONSECUTIVE_LOSSES = "max_consecutive_losses"
    MAX_DAILY_LOSS_AMOUNT = "max_daily_loss_amount"
    MAX_DAILY_LOSS_PERCENT = "max_daily_loss_percent"
    MAX_DAILY_PROFIT_TARGET = "max_daily_profit_target"
    COOLDOWN_AFTER_LOSS = "cooldown_after_loss"
    MAX_SIMULTANEOUS_POSITIONS = "max_simultaneous_positions"
    MINIMUM_CONFIDENCE = "minimum_confidence"
    SESSION_RESTRICTED = "session_restricted"
    SYMBOL_NOT_ALLOWED = "symbol_not_allowed"
    TIMEFRAME_NOT_ALLOWED = "timeframe_not_allowed"
    INVALID_SIGNAL = "invalid_signal"


@dataclass(frozen=True)
class RiskValidationResult:
    """Structured outcome of a risk validation request."""

    approved: bool
    timestamp: datetime
    reason: RiskRejectionReason | None = None
    message: str = ""
    rule_name: str | None = None
    state_snapshot: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def approved_result(
        cls,
        timestamp: datetime,
        state_snapshot: dict[str, Any],
    ) -> "RiskValidationResult":
        """Create an approved validation result."""
        return cls(approved=True, timestamp=timestamp, state_snapshot=state_snapshot)

    @classmethod
    def rejected_result(
        cls,
        timestamp: datetime,
        reason: RiskRejectionReason,
        message: str,
        rule_name: str,
        state_snapshot: dict[str, Any],
    ) -> "RiskValidationResult":
        """Create a rejected validation result."""
        return cls(
            approved=False,
            timestamp=timestamp,
            reason=reason,
            message=message,
            rule_name=rule_name,
            state_snapshot=state_snapshot,
        )


@dataclass(frozen=True)
class RiskEvent:
    """Represents an auditable risk event."""

    timestamp: datetime
    strategy_name: str
    symbol: str
    timeframe: str
    approved: bool
    reason: RiskRejectionReason | None
    message: str
    state_snapshot: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable event dictionary."""
        row = asdict(self)
        row["timestamp"] = self.timestamp.isoformat()
        row["reason"] = self.reason.value if self.reason else None
        return row


@dataclass
class DailyRiskState:
    """Tracks daily risk state isolated from strategy logic."""

    date: str
    trades_taken: int = 0
    wins: int = 0
    losses: int = 0
    blocked_trades: int = 0
    current_loss_streak: int = 0
    max_loss_streak: int = 0
    current_win_streak: int = 0
    realized_pnl: float = 0.0
    starting_balance: float = 0.0
    active_positions: int = 0
    cooldown_until: datetime | None = None
    strategy_cooldowns: dict[str, datetime] = field(default_factory=dict)
    rejection_counts: dict[str, int] = field(default_factory=dict)
    risk_shutdown_events: list[str] = field(default_factory=list)
    cooldown_events: int = 0

    def snapshot(self) -> dict[str, Any]:
        """Return a serializable snapshot of current daily state."""
        return {
            "date": self.date,
            "trades_taken": self.trades_taken,
            "wins": self.wins,
            "losses": self.losses,
            "blocked_trades": self.blocked_trades,
            "current_loss_streak": self.current_loss_streak,
            "max_loss_streak": self.max_loss_streak,
            "current_win_streak": self.current_win_streak,
            "realized_pnl": round(self.realized_pnl, 4),
            "starting_balance": round(self.starting_balance, 4),
            "active_positions": self.active_positions,
            "cooldown_until": self.cooldown_until.isoformat() if self.cooldown_until else None,
            "strategy_cooldowns": {
                strategy: timestamp.isoformat()
                for strategy, timestamp in self.strategy_cooldowns.items()
            },
            "rejection_counts": dict(self.rejection_counts),
            "risk_shutdown_events": list(self.risk_shutdown_events),
            "cooldown_events": self.cooldown_events,
        }
