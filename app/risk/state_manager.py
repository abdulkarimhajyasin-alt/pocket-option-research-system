"""Risk state management and daily reset logic."""

from datetime import UTC, datetime, timedelta

from loguru import logger

from app.backtesting.models import TradeOutcome
from app.risk.exposure import ExposureTracker
from app.risk.models import DailyRiskState, RiskRejectionReason
from app.signals.signal import TradeSignal


class RiskStateManager:
    """Owns mutable daily risk state and exposure tracking."""

    def __init__(self, starting_balance: float = 0.0) -> None:
        today = datetime.now(tz=UTC).date().isoformat()
        self.state = DailyRiskState(date=today, starting_balance=starting_balance)
        self.exposure = ExposureTracker()

    def ensure_date(self, timestamp: datetime) -> None:
        """Reset daily state when a new UTC date is encountered."""
        date_key = timestamp.astimezone(UTC).date().isoformat()
        if date_key != self.state.date:
            logger.info("Resetting risk state from {} to {}", self.state.date, date_key)
            self.state = DailyRiskState(
                date=date_key,
                starting_balance=self.state.starting_balance,
            )

    def record_approval(self, signal: TradeSignal) -> None:
        """Record risk approval before simulated execution."""
        self.ensure_date(signal.timestamp)
        self.state.trades_taken += 1

    def record_rejection(self, reason: RiskRejectionReason) -> None:
        """Record a blocked trade and its reason."""
        self.state.blocked_trades += 1
        reason_key = reason.value
        self.state.rejection_counts[reason_key] = self.state.rejection_counts.get(reason_key, 0) + 1
        if reason in {
            RiskRejectionReason.MAX_DAILY_LOSS_AMOUNT,
            RiskRejectionReason.MAX_DAILY_LOSS_PERCENT,
            RiskRejectionReason.MAX_DAILY_PROFIT_TARGET,
        }:
            self.state.risk_shutdown_events.append(reason_key)

    def record_trade_outcome(
        self,
        outcome: TradeOutcome,
        pnl: float,
        timestamp: datetime,
        strategy_name: str | None = None,
        loss_cooldown_minutes: int = 0,
        streak_cooldown_minutes: int = 0,
        consecutive_loss_trigger: int = 0,
    ) -> None:
        """Update streaks, PnL, and cooldowns after a simulated trade closes."""
        self.ensure_date(timestamp)
        if outcome == TradeOutcome.SKIPPED:
            return

        self.state.realized_pnl += pnl
        if outcome == TradeOutcome.WIN:
            self.state.wins += 1
            self.state.current_win_streak += 1
            self.state.current_loss_streak = 0
            return

        if outcome == TradeOutcome.LOSS:
            self.state.losses += 1
            self.state.current_loss_streak += 1
            self.state.max_loss_streak = max(
                self.state.max_loss_streak,
                self.state.current_loss_streak,
            )
            self.state.current_win_streak = 0
            self._start_cooldown(timestamp, loss_cooldown_minutes, strategy_name)
            if (
                consecutive_loss_trigger > 0
                and self.state.current_loss_streak >= consecutive_loss_trigger
            ):
                self._start_cooldown(timestamp, streak_cooldown_minutes, strategy_name)

    def _start_cooldown(
        self,
        timestamp: datetime,
        duration_minutes: int,
        strategy_name: str | None,
    ) -> None:
        if duration_minutes <= 0:
            return

        cooldown_until = timestamp.astimezone(UTC) + timedelta(minutes=duration_minutes)
        if self.state.cooldown_until is None or cooldown_until > self.state.cooldown_until:
            self.state.cooldown_until = cooldown_until
        if strategy_name:
            current = self.state.strategy_cooldowns.get(strategy_name)
            if current is None or cooldown_until > current:
                self.state.strategy_cooldowns[strategy_name] = cooldown_until
        self.state.cooldown_events += 1
        logger.info("Risk cooldown active until {}", cooldown_until)

    def open_position(self, trade_id: str, signal: TradeSignal) -> None:
        """Track an active position."""
        self.exposure.register(trade_id, signal)
        self.state.active_positions = self.exposure.total_active()

    def close_position(self, trade_id: str) -> None:
        """Close an active tracked position."""
        self.exposure.close(trade_id)
        self.state.active_positions = self.exposure.total_active()

    def snapshot(self) -> dict[str, object]:
        """Return a combined state and exposure snapshot."""
        return {
            **self.state.snapshot(),
            "exposure": self.exposure.snapshot(),
        }
