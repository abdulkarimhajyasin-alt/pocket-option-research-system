"""Lifecycle quality and record construction engines."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from app.trade_lifecycle.entry import EntryAnalysisEngine
from app.trade_lifecycle.expiry import ExpiryAnalysisEngine
from app.trade_lifecycle.models import LifecycleQuality, TradeLifecycleRecord
from app.trade_lifecycle.outcome import OutcomeEvaluationEngine
from app.trade_lifecycle.post_trade import FailureAnalysisEngine
from app.trade_lifecycle.post_trade import PostTradeIntelligenceEngine
from app.trade_lifecycle.post_trade import SuccessAnalysisEngine
from app.trade_lifecycle.state_machine import LifecycleStateMachine


class LifecycleQualityEngine:
    """Score lifecycle research quality without profitability claims."""

    def evaluate(
        self,
        lifecycle_score: float,
        confluence_score: float,
        confirmation_quality: float,
        performance_quality: float,
    ) -> LifecycleQuality:
        score = round(
            lifecycle_score * 0.35
            + confluence_score * 0.25
            + confirmation_quality * 0.20
            + performance_quality * 0.20,
            2,
        )
        return LifecycleQuality(
            score=max(0.0, min(100.0, score)),
            classification=self._classification(score),
            readiness=self._readiness(score),
            explanation="درجة جودة بحثية لدورة حياة الفرصة وليست توصية تداول.",
        )

    def _classification(self, score: float) -> str:
        if score >= 95:
            return "استثنائية"
        if score >= 85:
            return "قوية جدا"
        if score >= 75:
            return "قوية"
        if score >= 60:
            return "متوسطة"
        if score >= 40:
            return "ضعيفة"
        return "مرفوضة"

    def _readiness(self, score: float) -> str:
        if score >= 75:
            return "جاهزة للمرحلة التالية"
        if score >= 50:
            return "تحتاج مزيدا من التحليل"
        return "غير مؤهلة"


class TradeLifecycleEngine:
    """Build full research lifecycle records from confluence decisions."""

    def __init__(self) -> None:
        self.entry = EntryAnalysisEngine()
        self.expiry = ExpiryAnalysisEngine()
        self.outcome = OutcomeEvaluationEngine()
        self.post_trade = PostTradeIntelligenceEngine()
        self.failure = FailureAnalysisEngine()
        self.success = SuccessAnalysisEngine()
        self.quality = LifecycleQualityEngine()
        self.state_machine = LifecycleStateMachine()

    def simulate(self, decision: dict[str, Any], index: int) -> TradeLifecycleRecord:
        confluence = decision.get("confluence", {})
        created = datetime.fromisoformat(str(confluence.get("timestamp")))
        entry = self.entry.evaluate(decision)
        expiry = self.expiry.evaluate(decision, entry.readiness_score)
        confluence_score = self._float(decision.get("confluence_score"))
        qualification = self._factor_metric(decision, "عامل الفرصة", "opportunity_score")
        timeframe = self._factor_metric(decision, "عامل الأطر الزمنية", "alignment_score")
        session = self._factor_metric(decision, "عامل الجلسة", "session_quality")
        performance = self._factor_score(decision, "عامل الأداء")
        outcome = self.outcome.evaluate(
            confluence_score=confluence_score,
            qualification_score=qualification,
            entry=entry,
            expiry=expiry,
        )
        rejected = outcome.outcome == "UNRESOLVED" or confluence_score < 35
        state = self.state_machine.build(outcome.outcome, created, rejected)
        completed = created + self._expiry_delta(expiry.expiry)
        quality = self.quality.evaluate(
            lifecycle_score=(entry.readiness_score + expiry.expiry_quality) / 2,
            confluence_score=confluence_score,
            confirmation_quality=timeframe,
            performance_quality=performance,
        )
        return TradeLifecycleRecord(
            lifecycle_id=f"lifecycle-{index + 1:04d}",
            opportunity_id=str(decision.get("opportunity_id", "")),
            signal_id=f"signal-{decision.get('opportunity_id', index + 1)}",
            asset=str(decision.get("asset", "")),
            classification=str(decision.get("classification", "")),
            confidence=self._confidence(decision),
            confluence_score=confluence_score,
            qualification_score=qualification,
            timeframe_score=timeframe,
            session_score=session,
            created_at=created,
            completed_at=completed,
            state=state,
            outcome=outcome,
            entry=entry,
            expiry=expiry,
            post_trade=self.post_trade.analyze(decision, outcome),
            failure_analysis=self.failure.analyze(decision, outcome),
            success_analysis=self.success.analyze(decision),
            quality=quality,
            metadata={
                "research_only": True,
                "not_execution": True,
                "not_order_simulation": True,
                "not_investment_advice": True,
            },
        )

    def _factor_metric(self, decision: dict[str, Any], name: str, metric: str) -> float:
        factor = self._factor(decision, name)
        metrics = factor.get("metrics", {}) if isinstance(factor, dict) else {}
        return self._float(metrics.get(metric))

    def _factor_score(self, decision: dict[str, Any], name: str) -> float:
        factor = self._factor(decision, name)
        return self._float(factor.get("score")) if isinstance(factor, dict) else 0.0

    def _factor(self, decision: dict[str, Any], name: str) -> dict[str, Any]:
        confluence = decision.get("confluence", {})
        factors = confluence.get("factors", []) if isinstance(confluence, dict) else []
        for factor in factors:
            if isinstance(factor, dict) and factor.get("name") == name:
                return factor
        return {}

    def _confidence(self, decision: dict[str, Any]) -> float:
        return self._factor_metric(decision, "عامل الإشارة", "signal_confidence")

    def _expiry_delta(self, expiry: str) -> timedelta:
        mapping = {
            "30 ثانية": timedelta(seconds=30),
            "1 دقيقة": timedelta(minutes=1),
            "2 دقيقة": timedelta(minutes=2),
            "3 دقائق": timedelta(minutes=3),
            "5 دقائق": timedelta(minutes=5),
        }
        return mapping.get(expiry, timedelta(minutes=1))

    def _float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
