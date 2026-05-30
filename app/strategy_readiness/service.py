"""Strategy readiness orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from app.confluence.service import ConfluenceService
from app.multi_timeframe.service import MultiTimeframeService
from app.opportunity_engine.service import OpportunityService
from app.signal_intelligence.service import SignalIntelligenceService
from app.signal_performance.service import SignalPerformanceService
from app.strategy_readiness.analytics import StrategyReadinessAnalytics
from app.strategy_readiness.diagnostics import StrategyDiagnosticsEngine
from app.strategy_readiness.gates import DeploymentGateEngine
from app.strategy_readiness.models import StrategyReadinessResult
from app.strategy_readiness.readiness import StrategyReadinessEngine
from app.strategy_readiness.recommendations import RecommendationEngine
from app.strategy_readiness.reports import StrategyReadinessReportWriter
from app.strategy_readiness.storage import StrategyReadinessStorage
from app.strategy_readiness.validation import GateRequirementsEngine
from app.strategy_readiness.validation import ResearchStabilityEngine
from app.trade_lifecycle.service import TradeLifecycleService


@dataclass(frozen=True)
class StrategyReadinessRunResult:
    """Result of one readiness evaluation run."""

    result: StrategyReadinessResult
    analytics: dict[str, Any]
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class StrategyReadinessService:
    """Evaluate research strategy maturity across the full pipeline."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.stability = ResearchStabilityEngine()
        self.readiness = StrategyReadinessEngine()
        self.gates = DeploymentGateEngine()
        self.requirements = GateRequirementsEngine()
        self.diagnostics = StrategyDiagnosticsEngine()
        self.recommendations = RecommendationEngine()
        self.analytics = StrategyReadinessAnalytics()
        self.storage = StrategyReadinessStorage(
            self.project_root / "storage" / "strategy_readiness"
        )
        self.reports = StrategyReadinessReportWriter(
            self.project_root / "reports" / "strategy_readiness"
        )

    def run(self) -> StrategyReadinessRunResult:
        inputs = self._collect_inputs()
        stability = self.stability.evaluate(inputs)
        readiness = self.readiness.evaluate(inputs, stability.score)
        gates = self.gates.evaluate(readiness.components, stability.score)
        requirements = self.requirements.evaluate(inputs, readiness.score)
        diagnostics = self.diagnostics.evaluate(readiness.components, gates)
        recommendations = self.recommendations.generate(
            readiness.components,
            diagnostics,
        )
        result = StrategyReadinessResult(
            strategy_id="research-strategy-readiness",
            timestamp=datetime.utcnow(),
            readiness=readiness,
            gates=gates,
            requirements=requirements,
            stability=stability,
            diagnostics=diagnostics,
            recommendations=recommendations,
            strengths=[
                key for key, value in readiness.components.items() if value >= 70
            ],
            weaknesses=[
                key for key, value in readiness.components.items() if value < 70
            ],
            metadata={
                "research_only": True,
                "not_execution": True,
                "not_deployment_approval": True,
                "not_investment_advice": True,
            },
        )
        analytics = self.analytics.summarize(result)
        storage_paths = self.storage.save(result, analytics)
        report_paths = self.reports.export(analytics)
        return StrategyReadinessRunResult(
            result=result,
            analytics=analytics,
            storage_paths=storage_paths,
            report_paths=report_paths,
        )

    def _collect_inputs(self) -> dict[str, Any]:
        signal = SignalIntelligenceService(self.project_root).run()
        performance = SignalPerformanceService(self.project_root).run()
        opportunities = OpportunityService(self.project_root).run()
        timeframe = MultiTimeframeService(self.project_root).run()
        confluence = ConfluenceService(self.project_root).run()
        lifecycle = TradeLifecycleService(self.project_root).run()
        return {
            "signal_summary": signal.analytics.get("summary", signal.analytics),
            "performance_summary": performance.analytics.get("summary", {}),
            "opportunity_summary": opportunities.analytics.get("summary", {}),
            "timeframe_summary": timeframe.analytics.get("summary", {}),
            "confluence_summary": confluence.analytics.get("summary", {}),
            "lifecycle_summary": lifecycle.analytics.get("summary", {}),
        }
