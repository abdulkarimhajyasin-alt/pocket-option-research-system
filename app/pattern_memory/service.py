"""Pattern memory service orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from app.pattern_memory.analytics import PatternAnalytics
from app.pattern_memory.learning import AdaptiveLearningEngine
from app.pattern_memory.memory import PatternMemoryBuilder
from app.pattern_memory.models import PatternMemoryResult
from app.pattern_memory.pattern_engine import PatternDiscoveryEngine
from app.pattern_memory.reports import PatternMemoryReportWriter
from app.pattern_memory.scoring import PatternQualityEngine, PatternRankingEngine
from app.pattern_memory.similarity import PatternSimilarityEngine
from app.pattern_memory.storage import PatternMemoryStorage


@dataclass(frozen=True)
class PatternMemoryRunResult:
    """Result of one pattern memory run."""

    result: PatternMemoryResult
    analytics: dict[str, Any]
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class PatternMemoryService:
    """Run adaptive learning over local research history only."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.memory = PatternMemoryBuilder(self.project_root)
        self.discovery = PatternDiscoveryEngine()
        self.similarity = PatternSimilarityEngine()
        self.quality = PatternQualityEngine()
        self.learning = AdaptiveLearningEngine()
        self.ranking = PatternRankingEngine()
        self.analytics = PatternAnalytics()
        self.storage = PatternMemoryStorage(self.project_root / "storage" / "pattern_memory")
        self.reports = PatternMemoryReportWriter(self.project_root / "reports" / "pattern_memory")

    def run(self) -> PatternMemoryRunResult:
        records = self.memory.build()
        patterns = self.discovery.discover(records)
        similarities = self.similarity.compare(records, patterns)
        quality_scores = self.quality.evaluate(patterns)
        insights = self.learning.learn(records, patterns)
        rankings = self.ranking.rank(records)
        result = PatternMemoryResult(
            timestamp=datetime.utcnow(),
            records=records,
            discovered_patterns=patterns,
            similarities=similarities,
            quality_scores=quality_scores,
            learning_insights=insights,
            rankings=rankings,
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
        return PatternMemoryRunResult(result, analytics, storage_paths, report_paths)
