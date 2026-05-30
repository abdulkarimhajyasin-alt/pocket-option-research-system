"""Strategy benchmark orchestration."""

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
from app.strategy_benchmark.analytics import StrategyBenchmarkAnalytics
from app.strategy_benchmark.benchmark import ImprovementDetectionEngine
from app.strategy_benchmark.benchmark import ResearchCertificationPreparationEngine
from app.strategy_benchmark.benchmark import ResearchRobustnessEngine
from app.strategy_benchmark.comparator import StrategyComparator
from app.strategy_benchmark.models import StrategyBenchmarkResult
from app.strategy_benchmark.profiles import default_benchmark_profiles
from app.strategy_benchmark.ranking import StrategyRankingEngine
from app.strategy_benchmark.recommendations import BenchmarkRecommendationEngine
from app.strategy_benchmark.reports import StrategyBenchmarkReportWriter
from app.strategy_benchmark.scoring import BenchmarkScoringEngine
from app.strategy_benchmark.storage import StrategyBenchmarkStorage
from app.strategy_readiness.service import StrategyReadinessService
from app.trade_lifecycle.service import TradeLifecycleService


@dataclass(frozen=True)
class StrategyBenchmarkRunResult:
    """Result of one benchmark run."""

    result: StrategyBenchmarkResult
    analytics: dict[str, Any]
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class StrategyBenchmarkService:
    """Compare strategy research profiles without execution or broker control."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.comparator = StrategyComparator()
        self.scoring = BenchmarkScoringEngine()
        self.improvements = ImprovementDetectionEngine()
        self.robustness = ResearchRobustnessEngine()
        self.ranking = StrategyRankingEngine()
        self.recommendations = BenchmarkRecommendationEngine()
        self.certification = ResearchCertificationPreparationEngine()
        self.analytics = StrategyBenchmarkAnalytics()
        self.storage = StrategyBenchmarkStorage(
            self.project_root / "storage" / "strategy_benchmark"
        )
        self.reports = StrategyBenchmarkReportWriter(
            self.project_root / "reports" / "strategy_benchmark"
        )

    def run(self) -> StrategyBenchmarkRunResult:
        profiles = default_benchmark_profiles()
        comparisons = self.comparator.compare(profiles, self._collect_inputs())
        scores = tuple(self.scoring.score(item) for item in comparisons)
        baseline = next(item for item in scores if item.profile_id == "current")
        robustness = self.robustness.evaluate(comparisons)
        improvements = self.improvements.evaluate(baseline, scores, comparisons)
        rankings = self.ranking.rank(comparisons, scores)
        recommendations = self.recommendations.generate(
            rankings,
            robustness,
            improvements,
        )
        best_score = next(item for item in scores if item.profile_id == rankings[0].profile_id)
        best_robustness = next(
            item for item in robustness if item.profile_id == rankings[0].profile_id
        )
        result = StrategyBenchmarkResult(
            timestamp=datetime.utcnow(),
            comparisons=comparisons,
            scores=scores,
            robustness=robustness,
            improvements=improvements,
            rankings=rankings,
            recommendations=recommendations,
            certification=self.certification.evaluate(best_score, best_robustness),
            metadata={
                "research_only": True,
                "not_execution": True,
                "not_broker_control": True,
                "not_account_interaction": True,
                "not_investment_advice": True,
                "not_profitability_claim": True,
            },
        )
        analytics = self.analytics.summarize(result)
        storage_paths = self.storage.save(result, analytics)
        report_paths = self.reports.export(analytics)
        return StrategyBenchmarkRunResult(result, analytics, storage_paths, report_paths)

    def _collect_inputs(self) -> dict[str, Any]:
        signal = SignalIntelligenceService(self.project_root).run()
        performance = SignalPerformanceService(self.project_root).run()
        opportunities = OpportunityService(self.project_root).run()
        timeframe = MultiTimeframeService(self.project_root).run()
        confluence = ConfluenceService(self.project_root).run()
        lifecycle = TradeLifecycleService(self.project_root).run()
        readiness = StrategyReadinessService(self.project_root).run()
        return {
            "signal_summary": signal.analytics.get("summary", signal.analytics),
            "performance_summary": performance.analytics.get("summary", {}),
            "opportunity_summary": opportunities.analytics.get("summary", {}),
            "timeframe_summary": timeframe.analytics.get("summary", {}),
            "confluence_summary": confluence.analytics.get("summary", {}),
            "lifecycle_summary": lifecycle.analytics.get("summary", {}),
            "readiness_summary": readiness.analytics.get("summary", {}),
        }
