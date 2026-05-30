"""Market regime service orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from app.market_regime.analytics import MarketRegimeAnalytics
from app.market_regime.detector import MarketRegimeDetector, RegimeCandleLoader
from app.market_regime.models import MarketRegimeRun
from app.market_regime.reports import MarketRegimeReportWriter
from app.market_regime.scoring import PatternRegimeAnalyzer
from app.market_regime.scoring import RegimeCompatibilityEngine
from app.market_regime.storage import MarketRegimeStorage
from app.market_regime.transition import TransitionDetectionEngine
from app.market_regime.trend import TrendStrengthEngine
from app.market_regime.volatility import VolatilityEngine


@dataclass(frozen=True)
class MarketRegimeRunResult:
    """Result of one market regime run."""

    result: MarketRegimeRun
    analytics: dict[str, Any]
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class MarketRegimeService:
    """Detect market regimes from local research data only."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.loader = RegimeCandleLoader(self.project_root)
        self.volatility = VolatilityEngine()
        self.trend = TrendStrengthEngine()
        self.transition = TransitionDetectionEngine()
        self.detector = MarketRegimeDetector()
        self.compatibility = RegimeCompatibilityEngine(self.project_root)
        self.patterns = PatternRegimeAnalyzer()
        self.analytics = MarketRegimeAnalytics()
        self.storage = MarketRegimeStorage(self.project_root / "storage" / "market_regime")
        self.reports = MarketRegimeReportWriter(self.project_root / "reports" / "market_regime")

    def run(self) -> MarketRegimeRunResult:
        candles = self.loader.load()
        volatility = self.volatility.evaluate(candles)
        trend = self.trend.evaluate(candles)
        transition = self.transition.evaluate(candles)
        regime = self.detector.classify(volatility, trend, transition)
        compatibility = self.compatibility.evaluate(regime)
        pattern_analysis = self.patterns.analyze(regime, compatibility)
        result = MarketRegimeRun(
            timestamp=datetime.utcnow(),
            regime=regime,
            compatibility=compatibility,
            pattern_analysis=pattern_analysis,
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
        return MarketRegimeRunResult(result, analytics, storage_paths, report_paths)
