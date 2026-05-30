"""Research operations orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from app.confluence.service import ConfluenceService
from app.research_ops.alerts import ResearchAlertEngine
from app.research_ops.analytics import ResearchOperationsAnalytics
from app.research_ops.executive_summary import ExecutiveSummaryEngine
from app.research_ops.models import ResearchOperationsResult
from app.research_ops.opportunity_monitor import OpportunityMonitor
from app.research_ops.readiness_monitor import ResearchHealthEngine
from app.research_ops.recommendations import NextActionEngine
from app.research_ops.recommendations import ResearchRecommendationEngine
from app.research_ops.reports import ResearchOperationsReportWriter
from app.research_ops.risk_monitor import RiskMonitor
from app.research_ops.storage import ResearchOperationsStorage
from app.research_ops.strategy_monitor import StrategyMonitor
from app.strategy_readiness.service import StrategyReadinessService
from app.trade_lifecycle.service import TradeLifecycleService


@dataclass(frozen=True)
class ResearchOperationsRunResult:
    """Result of one research operations run."""

    result: ResearchOperationsResult
    analytics: dict[str, Any]
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class ResearchOperationsService:
    """Build the executive command layer for the research platform."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.strategy_monitor = StrategyMonitor()
        self.opportunity_monitor = OpportunityMonitor()
        self.risk_monitor = RiskMonitor()
        self.alerts = ResearchAlertEngine()
        self.recommendations = ResearchRecommendationEngine()
        self.next_action = NextActionEngine()
        self.health = ResearchHealthEngine()
        self.summary = ExecutiveSummaryEngine()
        self.analytics = ResearchOperationsAnalytics()
        self.storage = ResearchOperationsStorage(
            self.project_root / "storage" / "research_ops"
        )
        self.reports = ResearchOperationsReportWriter(
            self.project_root / "reports" / "research_ops"
        )

    def run(self) -> ResearchOperationsRunResult:
        inputs = self._collect_inputs()
        strategy = self.strategy_monitor.evaluate(
            inputs["strategy_readiness"],
            inputs["trade_lifecycle"],
        )
        opportunity = self.opportunity_monitor.evaluate(
            inputs["confluence"],
            inputs["trade_lifecycle"],
        )
        risk = self.risk_monitor.evaluate(strategy, opportunity.opportunity_count)
        alerts = self.alerts.generate(strategy, risk)
        health = self.health.evaluate(
            strategy.readiness_score,
            strategy.confidence_stability,
            len(alerts),
        )
        recommendations = self.recommendations.generate(alerts, risk)
        next_action = self.next_action.decide(recommendations, risk)
        executive = self.summary.build(
            strategy,
            opportunity,
            health,
            risk,
            alerts,
            recommendations,
            next_action,
        )
        result = ResearchOperationsResult(
            timestamp=datetime.utcnow(),
            executive_summary=executive,
            strategy_status=strategy,
            opportunity_status=opportunity,
            risk_assessment=risk,
            alerts=alerts,
            recommendations=recommendations,
            metadata={
                "research_only": True,
                "not_execution": True,
                "not_investment_advice": True,
                "not_profitability_claim": True,
            },
        )
        analytics = self.analytics.summarize(result)
        storage_paths = self.storage.save(result, analytics)
        report_paths = self.reports.export(analytics)
        return ResearchOperationsRunResult(
            result=result,
            analytics=analytics,
            storage_paths=storage_paths,
            report_paths=report_paths,
        )

    def _collect_inputs(self) -> dict[str, Any]:
        readiness = StrategyReadinessService(self.project_root).run()
        lifecycle = TradeLifecycleService(self.project_root).run()
        confluence = ConfluenceService(self.project_root).run()
        return {
            "strategy_readiness": readiness.analytics,
            "trade_lifecycle": lifecycle.analytics,
            "confluence": confluence.analytics,
        }
