"""Safety gate framework for simulated execution."""

from __future__ import annotations

from dataclasses import dataclass

from app.execution_simulator.models import BinaryOutcome, SimulatedTrade
from app.signals.signal import TradeSignal


@dataclass(frozen=True)
class SafetyGateConfig:
    """Configurable simulation-only safety limits."""

    max_daily_trades: int = 50
    max_consecutive_losses: int = 4
    max_drawdown: float = 8.0
    minimum_confidence: float = 0.60
    minimum_research_score: int = 40


@dataclass(frozen=True)
class SafetyGateResult:
    """Safety gate approval result."""

    approved: bool
    reason: str | None = None


class SafetyGateService:
    """Stateful safety gate evaluator for one simulation run."""

    def __init__(self, config: SafetyGateConfig | None = None) -> None:
        self.config = config or SafetyGateConfig()
        self.trades_taken = 0
        self.consecutive_losses = 0
        self.equity = 0.0
        self.peak_equity = 0.0

    def evaluate_signal(self, signal: TradeSignal) -> SafetyGateResult:
        """Return whether a signal may be simulated."""
        if self.trades_taken >= self.config.max_daily_trades:
            return SafetyGateResult(False, "max_daily_trades")
        if self.consecutive_losses >= self.config.max_consecutive_losses:
            return SafetyGateResult(False, "max_consecutive_losses")
        if self.current_drawdown >= self.config.max_drawdown:
            return SafetyGateResult(False, "max_drawdown")
        if signal.confidence < self.config.minimum_confidence:
            return SafetyGateResult(False, "minimum_confidence")
        return SafetyGateResult(True)

    def record_trade(self, trade: SimulatedTrade) -> None:
        """Update state after an executed simulated trade."""
        if trade.outcome not in {BinaryOutcome.WIN, BinaryOutcome.LOSS, BinaryOutcome.DRAW}:
            return
        self.trades_taken += 1
        self.equity += trade.profit_loss
        self.peak_equity = max(self.peak_equity, self.equity)
        if trade.outcome == BinaryOutcome.LOSS:
            self.consecutive_losses += 1
        elif trade.outcome == BinaryOutcome.WIN:
            self.consecutive_losses = 0

    @property
    def current_drawdown(self) -> float:
        """Return absolute drawdown from simulation equity peak."""
        return max(0.0, self.peak_equity - self.equity)
