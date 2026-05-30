"""Strategy-to-execution simulation lab orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.dashboard.decision import health_score, research_decision
from app.dashboard.service import DashboardService
from app.data.csv_loader import CsvCandleLoader
from app.execution_simulator.analytics import SimulationAnalytics
from app.execution_simulator.engine import ExecutionSimulator
from app.execution_simulator.models import (
    ExpiryDuration,
    SimulatedExecutionResult,
    SimulatedTrade,
)
from app.execution_simulator.reports import ExecutionSimulationReporter
from app.safety.gates import SafetyGateConfig, SafetyGateService
from app.strategies.sample_strategy import SampleCandleDirectionStrategy


@dataclass(frozen=True)
class ResearchReadinessResult:
    """Readiness decision before simulation starts."""

    approved: bool
    reason: str
    health_score: int
    decision_status: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "approved": self.approved,
            "reason": self.reason,
            "health_score": self.health_score,
            "decision_status": self.decision_status,
        }


class ExecutionSimulationLab:
    """Run a complete offline strategy-to-execution simulation."""

    def __init__(
        self,
        project_root: Path | str = ".",
        safety_config: SafetyGateConfig | None = None,
    ) -> None:
        self.project_root = Path(project_root)
        self.safety_config = safety_config or SafetyGateConfig()

    def run(
        self,
        run_name: str = "sample_execution_simulation",
        expiry: ExpiryDuration = ExpiryDuration.MINUTES_1,
    ) -> SimulatedExecutionResult:
        """Run the local simulation and export reports."""
        readiness = self.research_readiness()
        if not readiness.approved:
            analytics = SimulationAnalytics().summarize([])
            reports = ExecutionSimulationReporter(
                self.project_root / "reports" / "execution"
            ).export([], analytics, run_name)
            return SimulatedExecutionResult(
                trades=[],
                analytics=analytics,
                reports=reports,
                readiness=readiness.to_dict(),
            )

        data_path = self.project_root / "data" / "sample_eurusd_m1.csv"
        candles = CsvCandleLoader().load(data_path, symbol="EURUSD", timeframe="1m")
        safety = SafetyGateService(self.safety_config)
        simulator = ExecutionSimulator(safety=safety, expiry=expiry)
        strategy = SampleCandleDirectionStrategy()
        trades: list[SimulatedTrade] = []
        for index, candle in enumerate(candles):
            signal = strategy.on_candle(
                {"current_candle": candle, "history": candles.history_until(index)}
            )
            if signal is None:
                continue
            trades.append(simulator.simulate_signal(signal, candles, index))
        analytics = SimulationAnalytics().summarize(trades)
        reports = ExecutionSimulationReporter(
            self.project_root / "reports" / "execution"
        ).export(trades, analytics, run_name)
        return SimulatedExecutionResult(
            trades=trades,
            analytics=analytics,
            reports=reports,
            readiness=readiness.to_dict(),
        )

    def research_readiness(self) -> ResearchReadinessResult:
        """Check dashboard research readiness before simulation."""
        overview = DashboardService(self.project_root).overview()
        decision = research_decision(overview)
        score = health_score(overview)
        if score.score < self.safety_config.minimum_research_score:
            return ResearchReadinessResult(
                approved=False,
                reason=(
                    "تم منع المحاكاة لأن درجة الجاهزية البحثية أقل من الحد المطلوب."
                ),
                health_score=score.score,
                decision_status=decision.status,
            )
        if decision.severity == "critical":
            return ResearchReadinessResult(
                approved=False,
                reason="تم منع المحاكاة لأن القرار البحثي الحالي مرفوض.",
                health_score=score.score,
                decision_status=decision.status,
            )
        return ResearchReadinessResult(
            approved=True,
            reason="تم السماح بالمحاكاة لأنها محلية وبحثية وتستوفي الحد الأدنى.",
            health_score=score.score,
            decision_status=decision.status,
        )
