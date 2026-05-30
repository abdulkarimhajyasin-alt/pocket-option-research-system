"""Unified confluence and research decision engines."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from app.confluence.liquidity_factor import LiquidityFactorEngine
from app.confluence.models import ConfluenceScore, FactorScore, ResearchDecision
from app.confluence.opportunity_factor import OpportunityFactorEngine
from app.confluence.performance_factor import PerformanceFactorEngine
from app.confluence.scoring import ConfluenceScoringEngine, ResearchReadinessEngine
from app.confluence.session_factor import SessionFactorEngine
from app.confluence.signal_factor import SignalFactorEngine
from app.confluence.timeframe_factor import TimeframeFactorEngine


class ConfluenceEngine:
    """Combine all research factors into one confluence assessment."""

    def __init__(self) -> None:
        self.signal = SignalFactorEngine()
        self.performance = PerformanceFactorEngine()
        self.opportunity = OpportunityFactorEngine()
        self.timeframe = TimeframeFactorEngine()
        self.session = SessionFactorEngine()
        self.liquidity = LiquidityFactorEngine()
        self.scoring = ConfluenceScoringEngine()

    def evaluate(
        self,
        opportunity: dict[str, Any],
        confirmation: dict[str, Any],
        signal_summary: dict[str, Any],
        performance_summary: dict[str, Any],
        session_performance: dict[str, Any],
    ) -> ConfluenceScore:
        factors = (
            self.signal.evaluate(opportunity, signal_summary),
            self.performance.evaluate(performance_summary),
            self.opportunity.evaluate(opportunity),
            self.timeframe.evaluate(confirmation),
            self.session.evaluate(opportunity, session_performance),
            self.liquidity.evaluate(opportunity),
        )
        score = self.scoring.score(factors)
        strengths, weaknesses, warnings = self._summarize_factors(factors)
        return ConfluenceScore(
            opportunity_id=str(opportunity.get("opportunity_id", "")),
            asset=str(opportunity.get("asset", "")),
            classification=str(opportunity.get("classification", "")),
            session=str(confirmation.get("session") or "غير متاح"),
            timestamp=datetime.fromisoformat(str(opportunity.get("timestamp"))),
            score=score,
            state=self._state(score),
            explanation=(
                "درجة توافق بحثية موحدة من عوامل الإشارة والأداء والفرصة."
            ),
            factors=factors,
            strengths=strengths,
            weaknesses=weaknesses,
            warnings=warnings,
            metadata={
                "research_only": True,
                "not_execution": True,
                "not_investment_advice": True,
                "not_profitability_claim": True,
            },
        )

    def _state(self, score: float) -> str:
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

    def _summarize_factors(
        self,
        factors: tuple[FactorScore, ...],
    ) -> tuple[list[str], list[str], list[str]]:
        strengths: list[str] = []
        weaknesses: list[str] = []
        warnings: list[str] = []
        for factor in factors:
            strengths.extend(factor.strengths)
            weaknesses.extend(factor.weaknesses)
            warnings.extend(factor.warnings)
            if factor.score < 45:
                warnings.append(f"{factor.name} منخفض")
        return strengths[:8], weaknesses[:8], warnings[:8]


class ResearchDecisionEngine:
    """Create final Arabic research decision output."""

    def __init__(self) -> None:
        self.readiness = ResearchReadinessEngine()

    def decide(self, confluence: ConfluenceScore) -> ResearchDecision:
        readiness = self.readiness.evaluate(confluence.score, confluence.factors)
        final_decision = self._decision(confluence.score, readiness)
        confidence = self._confidence(confluence.score)
        return ResearchDecision(
            opportunity_id=confluence.opportunity_id,
            asset=confluence.asset,
            classification=confluence.classification,
            final_decision=final_decision,
            confluence_score=confluence.score,
            confidence_level=confidence,
            acceptance_reasons=confluence.strengths[:5],
            rejection_reasons=confluence.weaknesses[:5],
            risk_factors=confluence.warnings[:5],
            readiness=readiness,
            confluence=confluence,
        )

    def _decision(self, score: float, readiness: str) -> str:
        if readiness == "غير مؤهلة" or score < 40:
            return "قرار بحثي نهائي: مرفوضة للبحث المتقدم"
        if score >= 75:
            return "قرار بحثي نهائي: صالحة للتحليل المتقدم"
        return "قرار بحثي نهائي: تحتاج مراجعة بحثية"

    def _confidence(self, score: float) -> str:
        if score >= 85:
            return "ثقة مرتفعة"
        if score >= 60:
            return "ثقة متوسطة"
        return "ثقة منخفضة"
