"""Signal intelligence orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.data.csv_loader import CsvCandleLoader
from app.data.models import Candle, CandleSeries
from app.signal_intelligence.analytics import SignalAnalytics
from app.signal_intelligence.cisd import CISDEngine
from app.signal_intelligence.confidence import ConfidenceEngine
from app.signal_intelligence.fvg import FVGEngine
from app.signal_intelligence.ifvg import IFVGEngine
from app.signal_intelligence.liquidity import LiquidityEngine
from app.signal_intelligence.models import (
    ResearchSignalClass,
    SignalIntelligenceResult,
    SignalIntelligenceSnapshot,
)
from app.signal_intelligence.reports import SignalReportWriter
from app.signal_intelligence.sessions import SessionEngine
from app.signal_intelligence.storage import SignalStorage
from app.signal_intelligence.structure import StructureEngine


@dataclass(frozen=True)
class SignalIntelligenceRunResult:
    """Result of one signal intelligence research cycle."""

    snapshot: SignalIntelligenceSnapshot
    analytics: dict[str, Any]
    storage_paths: dict[str, str]
    report_paths: dict[str, str]


class SignalIntelligenceService:
    """Detect, score, validate, and explain research signal classifications."""

    def __init__(self, project_root: Path | str = ".") -> None:
        self.project_root = Path(project_root)
        self.structure = StructureEngine()
        self.cisd = CISDEngine()
        self.fvg = FVGEngine()
        self.ifvg = IFVGEngine()
        self.liquidity = LiquidityEngine()
        self.sessions = SessionEngine()
        self.confidence = ConfidenceEngine()
        self.analytics = SignalAnalytics()
        self.storage = SignalStorage(self.project_root / "storage" / "signals")
        self.reports = SignalReportWriter(self.project_root / "reports" / "signals")

    def run(self) -> SignalIntelligenceRunResult:
        candles = self._load_candles()
        signals = self.analyze(candles)
        analytics = self.analytics.summarize(signals)
        snapshot = SignalIntelligenceSnapshot(
            timestamp=candles.last.timestamp if candles.last else signals[-1].timestamp,
            asset=candles.symbol,
            timeframe=candles.timeframe,
            candles=tuple(candles),
            signals=tuple(signals),
            analytics=analytics,
        )
        storage_paths = self.storage.save(signals, analytics)
        report_paths = self.reports.export(analytics)
        return SignalIntelligenceRunResult(snapshot, analytics, storage_paths, report_paths)

    def analyze(self, candles: CandleSeries) -> list[SignalIntelligenceResult]:
        results: list[SignalIntelligenceResult] = []
        for index in range(6, len(candles)):
            history = list(candles.history_until(index))
            results.append(self._classify(history))
        return results

    def _classify(self, candles: list[Candle]) -> SignalIntelligenceResult:
        current = candles[-1]
        structure = self.structure.detect(candles)
        cisd = self.cisd.detect(candles)
        fvg = self.fvg.detect(candles)
        ifvg = self.ifvg.detect(candles, fvg)
        liquidity = self.liquidity.detect(candles)
        session = self.sessions.detect(current)
        confidence = self.confidence.score(structure, cisd, fvg, ifvg, liquidity, session)
        classification = self._classification(structure.state, cisd.direction, confidence.score)
        supporting, rejection = self._factors(structure, cisd, fvg, ifvg, liquidity, session)
        return SignalIntelligenceResult(
            timestamp=current.timestamp,
            asset=current.symbol,
            timeframe=current.timeframe,
            classification=classification,
            confidence=confidence,
            explanation="تصنيف بحثي مبني على الهيكل السعري ومكونات حركة السعر.",
            supporting_factors=supporting,
            rejection_factors=rejection,
            structure=structure,
            cisd=cisd,
            fvg=fvg,
            ifvg=ifvg,
            liquidity=liquidity,
            session=session,
            metadata={
                "research_only": True,
                "not_execution": True,
                "not_investment_advice": True,
            },
        )

    def _classification(
        self,
        structure_state: str,
        cisd_direction: str,
        confidence_score: float,
    ) -> ResearchSignalClass:
        if confidence_score < 40:
            return ResearchSignalClass.NO_TRADE
        if structure_state == "هيكل صاعد" and cisd_direction == "صاعد":
            return ResearchSignalClass.CALL
        if structure_state == "هيكل هابط" and cisd_direction == "هابط":
            return ResearchSignalClass.PUT
        return ResearchSignalClass.NO_TRADE

    def _factors(
        self,
        structure,
        cisd,
        fvg,
        ifvg,
        liquidity,
        session,
    ) -> tuple[list[str], list[str]]:
        supporting = [structure.state, cisd.explanation, session.session_name]
        if fvg:
            supporting.append(f"فجوة قيمة عادلة {fvg.direction}")
        if ifvg and ifvg.confirmed:
            supporting.append("انعكاس فجوة مؤكد")
        if liquidity.sweep_confirmed:
            supporting.append(liquidity.sweep_direction)
        warnings = []
        if not cisd.validated:
            warnings.append("تغير الحالة غير مؤكد")
        if fvg is None:
            warnings.append("لا توجد فجوة قيمة عادلة حديثة")
        if not liquidity.sweep_confirmed:
            warnings.append("السيولة القريبة غير مؤكدة")
        return supporting, warnings

    def _load_candles(self) -> CandleSeries:
        path = self.project_root / "data" / "sample_eurusd_m1.csv"
        if not path.exists():
            path = Path(__file__).resolve().parents[2] / "data" / "sample_eurusd_m1.csv"
        return CsvCandleLoader().load(path, symbol="EURUSD", timeframe="1m")
