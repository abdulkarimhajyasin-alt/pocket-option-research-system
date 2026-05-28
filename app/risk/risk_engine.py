"""Rule-driven risk engine with final execution approval authority."""

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from loguru import logger

from app.backtesting.models import TradeOutcome
from app.risk.models import RiskEvent, RiskRejectionReason, RiskValidationResult
from app.risk.rules import (
    CooldownAfterLossRule,
    MaxConsecutiveLossesRule,
    MaxDailyLossAmountRule,
    MaxDailyLossPercentRule,
    MaxDailyProfitTargetRule,
    MaxSimultaneousPositionsRule,
    MaxTradesPerDayRule,
    MinimumConfidenceRule,
    RiskRule,
    RiskRuleContext,
    SessionRestrictionRule,
    SymbolWhitelistRule,
    TimeframeWhitelistRule,
)
from app.risk.state_manager import RiskStateManager
from app.signals.signal import TradeSignal

risk_event_logger = logger.bind(component="risk")


@dataclass(frozen=True)
class RiskConfig:
    """Configurable risk controls used to build rule sets."""

    starting_balance: float = 10_000.0
    max_trades_per_day: int = 50
    max_consecutive_losses: int = 5
    max_daily_loss_amount: float = 250.0
    max_daily_loss_percent: float = 0.03
    max_daily_profit_target: float = 500.0
    loss_cooldown_minutes: int = 0
    consecutive_loss_cooldown_minutes: int = 0
    consecutive_loss_cooldown_trigger: int = 3
    max_simultaneous_positions: int = 1
    min_confidence: float = 0.60
    allowed_sessions: tuple[str, ...] = ()
    allowed_symbols: tuple[str, ...] = ()
    allowed_timeframes: tuple[str, ...] = ()
    enabled_rules: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """Validate risk profile values."""
        if self.starting_balance < 0:
            raise ValueError("starting_balance cannot be negative")
        if not 0.0 <= self.min_confidence <= 1.0:
            raise ValueError("min_confidence must be between 0 and 1")
        if self.max_daily_loss_percent < 0:
            raise ValueError("max_daily_loss_percent cannot be negative")

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "RiskConfig":
        """Build config from a dictionary with defaults."""
        return cls(
            starting_balance=float(raw.get("starting_balance", 10_000.0)),
            max_trades_per_day=int(raw.get("max_trades_per_day", 50)),
            max_consecutive_losses=int(raw.get("max_consecutive_losses", 5)),
            max_daily_loss_amount=float(raw.get("max_daily_loss_amount", 250.0)),
            max_daily_loss_percent=float(raw.get("max_daily_loss_percent", 0.03)),
            max_daily_profit_target=float(raw.get("max_daily_profit_target", 500.0)),
            loss_cooldown_minutes=int(raw.get("loss_cooldown_minutes", 0)),
            consecutive_loss_cooldown_minutes=int(
                raw.get("consecutive_loss_cooldown_minutes", 0)
            ),
            consecutive_loss_cooldown_trigger=int(
                raw.get("consecutive_loss_cooldown_trigger", 3)
            ),
            max_simultaneous_positions=int(raw.get("max_simultaneous_positions", 1)),
            min_confidence=float(raw.get("min_confidence", 0.60)),
            allowed_sessions=tuple(raw.get("allowed_sessions", [])),
            allowed_symbols=tuple(raw.get("allowed_symbols", [])),
            allowed_timeframes=tuple(raw.get("allowed_timeframes", [])),
            enabled_rules=tuple(raw.get("enabled_rules", [])),
        )

    @classmethod
    def from_yaml(cls, path: Path | str) -> "RiskConfig":
        """Load a risk config profile from YAML."""
        config_path = Path(path)
        logger.info("Loading risk profile from {}", config_path)
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        return cls.from_dict(raw)


class RiskEngine:
    """Evaluates signals against risk rules and owns final approval."""

    def __init__(
        self,
        min_confidence: float = 0.60,
        config: RiskConfig | None = None,
        rules: Sequence[RiskRule] | None = None,
        state_manager: RiskStateManager | None = None,
    ) -> None:
        self.config = config or RiskConfig(min_confidence=min_confidence)
        self.state_manager = state_manager or RiskStateManager(self.config.starting_balance)
        self.rules = list(rules) if rules is not None else self._build_default_rules(self.config)
        self.events: list[RiskEvent] = []
        logger.info("Risk engine initialized with {} rules", len(self.rules))

    @classmethod
    def from_profile(cls, path: Path | str) -> "RiskEngine":
        """Create a risk engine from a YAML profile."""
        config = RiskConfig.from_yaml(path)
        return cls(config=config)

    def assess_signal(self, signal: TradeSignal) -> RiskValidationResult:
        """Return a structured risk validation result for a signal."""
        self.state_manager.ensure_date(signal.timestamp)
        context = RiskRuleContext(
            signal=signal,
            state=self.state_manager.state,
            state_snapshot=self.state_manager.snapshot(),
            exposure_snapshot=self.state_manager.exposure.snapshot(),
        )

        if not signal.symbol.strip() or not signal.timeframe.strip():
            result = RiskValidationResult.rejected_result(
                timestamp=signal.timestamp,
                reason=RiskRejectionReason.INVALID_SIGNAL,
                message="Signal symbol and timeframe are required",
                rule_name="signal_integrity",
                state_snapshot=context.state_snapshot,
            )
            self._record_result(signal, result)
            return result

        for rule in self.rules:
            result = rule.evaluate(context)
            if not result.approved:
                self._record_result(signal, result)
                return result

        result = RiskValidationResult.approved_result(
            timestamp=signal.timestamp,
            state_snapshot=self.state_manager.snapshot(),
        )
        self.state_manager.record_approval(signal)
        self._record_result(signal, result)
        return result

    def validate_signal(self, signal: TradeSignal) -> bool:
        """Return True when the Risk Engine approves the signal."""
        return self.assess_signal(signal).approved

    def record_trade_result(
        self,
        outcome: TradeOutcome,
        pnl: float,
        timestamp: datetime,
        strategy_name: str | None = None,
    ) -> None:
        """Update risk state after a trade outcome is known."""
        self.state_manager.record_trade_outcome(
            outcome=outcome,
            pnl=pnl,
            timestamp=timestamp,
            strategy_name=strategy_name,
            loss_cooldown_minutes=self.config.loss_cooldown_minutes,
            streak_cooldown_minutes=self.config.consecutive_loss_cooldown_minutes,
            consecutive_loss_trigger=self.config.consecutive_loss_cooldown_trigger,
        )

    def state_snapshot(self) -> dict[str, object]:
        """Return the current risk state snapshot."""
        return self.state_manager.snapshot()

    def _build_default_rules(self, config: RiskConfig) -> list[RiskRule]:
        enabled = set(config.enabled_rules)

        def is_enabled(name: str) -> bool:
            return not enabled or name in enabled

        return [
            MaxTradesPerDayRule(config.max_trades_per_day, is_enabled("max_trades_per_day")),
            MaxConsecutiveLossesRule(
                config.max_consecutive_losses,
                is_enabled("max_consecutive_losses"),
            ),
            MaxDailyLossAmountRule(
                config.max_daily_loss_amount,
                is_enabled("max_daily_loss_amount"),
            ),
            MaxDailyLossPercentRule(
                config.max_daily_loss_percent,
                is_enabled("max_daily_loss_percent"),
            ),
            MaxDailyProfitTargetRule(
                config.max_daily_profit_target,
                is_enabled("max_daily_profit_target"),
            ),
            CooldownAfterLossRule(is_enabled("cooldown_after_loss")),
            MaxSimultaneousPositionsRule(
                config.max_simultaneous_positions,
                is_enabled("max_simultaneous_positions"),
            ),
            MinimumConfidenceRule(config.min_confidence, is_enabled("minimum_confidence")),
            SessionRestrictionRule(
                config.allowed_sessions,
                is_enabled("session_restriction"),
            ),
            SymbolWhitelistRule(config.allowed_symbols, is_enabled("symbol_whitelist")),
            TimeframeWhitelistRule(
                config.allowed_timeframes,
                is_enabled("timeframe_whitelist"),
            ),
        ]

    def _record_result(self, signal: TradeSignal, result: RiskValidationResult) -> None:
        event = RiskEvent(
            timestamp=result.timestamp,
            strategy_name=signal.strategy_name,
            symbol=signal.symbol,
            timeframe=signal.timeframe,
            approved=result.approved,
            reason=result.reason,
            message=result.message,
            state_snapshot=result.state_snapshot,
        )
        self.events.append(event)

        if result.approved:
            risk_event_logger.info(
                "Risk approved signal strategy={} symbol={} timestamp={}",
                signal.strategy_name,
                signal.symbol,
                result.timestamp,
            )
            return

        if result.reason is not None:
            self.state_manager.record_rejection(result.reason)
        risk_event_logger.warning(
            "Risk rejected signal strategy={} symbol={} reason={} timestamp={} state={}",
            signal.strategy_name,
            signal.symbol,
            result.reason.value if result.reason else None,
            result.timestamp.astimezone(UTC).isoformat(),
            result.state_snapshot,
        )
