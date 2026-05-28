"""Reusable risk rule architecture."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC

from app.risk.models import DailyRiskState, RiskRejectionReason, RiskValidationResult
from app.signals.session_filter import SessionFilter
from app.signals.signal import TradeSignal


@dataclass(frozen=True)
class RiskRuleContext:
    """Context passed into each risk rule evaluation."""

    signal: TradeSignal
    state: DailyRiskState
    state_snapshot: dict[str, object]
    exposure_snapshot: dict[str, int]


class RiskRule(ABC):
    """Base class for individually testable risk rules."""

    name: str
    enabled: bool = True

    @abstractmethod
    def evaluate(self, context: RiskRuleContext) -> RiskValidationResult:
        """Evaluate a signal against this rule."""

    def approve(self, context: RiskRuleContext) -> RiskValidationResult:
        """Return an approved result for this rule."""
        return RiskValidationResult.approved_result(
            timestamp=context.signal.timestamp,
            state_snapshot=context.state_snapshot,
        )

    def reject(
        self,
        context: RiskRuleContext,
        reason: RiskRejectionReason,
        message: str,
    ) -> RiskValidationResult:
        """Return a rejected result for this rule."""
        return RiskValidationResult.rejected_result(
            timestamp=context.signal.timestamp,
            reason=reason,
            message=message,
            rule_name=self.name,
            state_snapshot=context.state_snapshot,
        )


class MaxTradesPerDayRule(RiskRule):
    """Blocks signals after a daily trade count limit."""

    name = "max_trades_per_day"

    def __init__(self, max_trades: int, enabled: bool = True) -> None:
        self.max_trades = max_trades
        self.enabled = enabled

    def evaluate(self, context: RiskRuleContext) -> RiskValidationResult:
        """Evaluate daily trade count."""
        if not self.enabled or self.max_trades <= 0:
            return self.approve(context)
        if context.state.trades_taken >= self.max_trades:
            return self.reject(
                context,
                RiskRejectionReason.MAX_TRADES_PER_DAY,
                f"Daily trade limit reached: {self.max_trades}",
            )
        return self.approve(context)


class MaxConsecutiveLossesRule(RiskRule):
    """Blocks signals after too many consecutive losses."""

    name = "max_consecutive_losses"

    def __init__(self, max_losses: int, enabled: bool = True) -> None:
        self.max_losses = max_losses
        self.enabled = enabled

    def evaluate(self, context: RiskRuleContext) -> RiskValidationResult:
        """Evaluate consecutive loss streak."""
        if not self.enabled or self.max_losses <= 0:
            return self.approve(context)
        if context.state.current_loss_streak >= self.max_losses:
            return self.reject(
                context,
                RiskRejectionReason.MAX_CONSECUTIVE_LOSSES,
                f"Consecutive loss limit reached: {self.max_losses}",
            )
        return self.approve(context)


class MaxDailyLossAmountRule(RiskRule):
    """Blocks signals once daily realized loss exceeds an amount."""

    name = "max_daily_loss_amount"

    def __init__(self, max_loss_amount: float, enabled: bool = True) -> None:
        self.max_loss_amount = max_loss_amount
        self.enabled = enabled

    def evaluate(self, context: RiskRuleContext) -> RiskValidationResult:
        """Evaluate absolute daily loss."""
        if not self.enabled or self.max_loss_amount <= 0:
            return self.approve(context)
        if context.state.realized_pnl <= -abs(self.max_loss_amount):
            return self.reject(
                context,
                RiskRejectionReason.MAX_DAILY_LOSS_AMOUNT,
                f"Daily loss amount limit reached: {self.max_loss_amount}",
            )
        return self.approve(context)


class MaxDailyLossPercentRule(RiskRule):
    """Blocks signals once daily realized loss exceeds account percentage."""

    name = "max_daily_loss_percent"

    def __init__(self, max_loss_percent: float, enabled: bool = True) -> None:
        self.max_loss_percent = max_loss_percent
        self.enabled = enabled

    def evaluate(self, context: RiskRuleContext) -> RiskValidationResult:
        """Evaluate daily loss as percentage of starting balance."""
        if not self.enabled or self.max_loss_percent <= 0 or context.state.starting_balance <= 0:
            return self.approve(context)
        loss_percent = abs(min(context.state.realized_pnl, 0.0)) / context.state.starting_balance
        if loss_percent >= self.max_loss_percent:
            return self.reject(
                context,
                RiskRejectionReason.MAX_DAILY_LOSS_PERCENT,
                f"Daily loss percent limit reached: {self.max_loss_percent}",
            )
        return self.approve(context)


class MaxDailyProfitTargetRule(RiskRule):
    """Blocks signals once daily profit target has been reached."""

    name = "max_daily_profit_target"

    def __init__(self, profit_target: float, enabled: bool = True) -> None:
        self.profit_target = profit_target
        self.enabled = enabled

    def evaluate(self, context: RiskRuleContext) -> RiskValidationResult:
        """Evaluate daily profit target."""
        if not self.enabled or self.profit_target <= 0:
            return self.approve(context)
        if context.state.realized_pnl >= self.profit_target:
            return self.reject(
                context,
                RiskRejectionReason.MAX_DAILY_PROFIT_TARGET,
                f"Daily profit target reached: {self.profit_target}",
            )
        return self.approve(context)


class CooldownAfterLossRule(RiskRule):
    """Blocks signals while global or strategy-specific cooldowns are active."""

    name = "cooldown_after_loss"

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled

    def evaluate(self, context: RiskRuleContext) -> RiskValidationResult:
        """Evaluate active cooldown windows."""
        if not self.enabled:
            return self.approve(context)
        timestamp = context.signal.timestamp.astimezone(UTC)
        global_until = context.state.cooldown_until
        strategy_until = context.state.strategy_cooldowns.get(context.signal.strategy_name)
        cooldown_until = max(
            [value for value in (global_until, strategy_until) if value is not None],
            default=None,
        )
        if cooldown_until is not None and timestamp < cooldown_until:
            return self.reject(
                context,
                RiskRejectionReason.COOLDOWN_AFTER_LOSS,
                f"Cooldown active until {cooldown_until.isoformat()}",
            )
        return self.approve(context)


class MaxSimultaneousPositionsRule(RiskRule):
    """Blocks signals when active position exposure is too high."""

    name = "max_simultaneous_positions"

    def __init__(self, max_positions: int, enabled: bool = True) -> None:
        self.max_positions = max_positions
        self.enabled = enabled

    def evaluate(self, context: RiskRuleContext) -> RiskValidationResult:
        """Evaluate active position count."""
        if not self.enabled or self.max_positions <= 0:
            return self.approve(context)
        if context.state.active_positions >= self.max_positions:
            return self.reject(
                context,
                RiskRejectionReason.MAX_SIMULTANEOUS_POSITIONS,
                f"Maximum simultaneous positions reached: {self.max_positions}",
            )
        return self.approve(context)


class MinimumConfidenceRule(RiskRule):
    """Blocks low-confidence signals."""

    name = "minimum_confidence"

    def __init__(self, min_confidence: float, enabled: bool = True) -> None:
        self.min_confidence = min_confidence
        self.enabled = enabled

    def evaluate(self, context: RiskRuleContext) -> RiskValidationResult:
        """Evaluate signal confidence."""
        if not self.enabled:
            return self.approve(context)
        if not 0.0 <= context.signal.confidence <= 1.0:
            return self.reject(
                context,
                RiskRejectionReason.INVALID_SIGNAL,
                "Signal confidence must be between 0 and 1",
            )
        if context.signal.confidence < self.min_confidence:
            return self.reject(
                context,
                RiskRejectionReason.MINIMUM_CONFIDENCE,
                f"Signal confidence below minimum: {self.min_confidence}",
            )
        return self.approve(context)


class SessionRestrictionRule(RiskRule):
    """Blocks signals outside configured sessions."""

    name = "session_restriction"

    def __init__(self, allowed_sessions: tuple[str, ...], enabled: bool = True) -> None:
        self.allowed_sessions = allowed_sessions
        self.enabled = enabled
        self.session_filter = SessionFilter()

    def evaluate(self, context: RiskRuleContext) -> RiskValidationResult:
        """Evaluate configured session windows."""
        if not self.enabled or not self.allowed_sessions:
            return self.approve(context)
        if not self.session_filter.is_allowed(context.signal.timestamp, self.allowed_sessions):
            return self.reject(
                context,
                RiskRejectionReason.SESSION_RESTRICTED,
                f"Signal outside allowed sessions: {self.allowed_sessions}",
            )
        return self.approve(context)


class SymbolWhitelistRule(RiskRule):
    """Blocks signals for symbols outside the whitelist."""

    name = "symbol_whitelist"

    def __init__(self, allowed_symbols: tuple[str, ...], enabled: bool = True) -> None:
        self.allowed_symbols = tuple(symbol.upper() for symbol in allowed_symbols)
        self.enabled = enabled

    def evaluate(self, context: RiskRuleContext) -> RiskValidationResult:
        """Evaluate symbol whitelist."""
        if not self.enabled or not self.allowed_symbols:
            return self.approve(context)
        if context.signal.symbol.upper() not in self.allowed_symbols:
            return self.reject(
                context,
                RiskRejectionReason.SYMBOL_NOT_ALLOWED,
                f"Symbol not allowed: {context.signal.symbol}",
            )
        return self.approve(context)


class TimeframeWhitelistRule(RiskRule):
    """Blocks signals for timeframes outside the whitelist."""

    name = "timeframe_whitelist"

    def __init__(self, allowed_timeframes: tuple[str, ...], enabled: bool = True) -> None:
        self.allowed_timeframes = allowed_timeframes
        self.enabled = enabled

    def evaluate(self, context: RiskRuleContext) -> RiskValidationResult:
        """Evaluate timeframe whitelist."""
        if not self.enabled or not self.allowed_timeframes:
            return self.approve(context)
        if context.signal.timeframe not in self.allowed_timeframes:
            return self.reject(
                context,
                RiskRejectionReason.TIMEFRAME_NOT_ALLOWED,
                f"Timeframe not allowed: {context.signal.timeframe}",
            )
        return self.approve(context)
