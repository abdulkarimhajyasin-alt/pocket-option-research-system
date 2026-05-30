"""Opportunity qualification scoring and deterministic decisions."""

from __future__ import annotations

from dataclasses import dataclass

from app.opportunity_engine.cisd_score import CISDScoreEngine
from app.opportunity_engine.fvg_score import FVGScoreEngine
from app.opportunity_engine.liquidity_score import LiquidityScoreEngine
from app.opportunity_engine.models import QualifiedOpportunity, ScoreBreakdown
from app.opportunity_engine.session_score import SessionScoreEngine
from app.opportunity_engine.structure_score import StructureScoreEngine


@dataclass(frozen=True)
class QualificationWeights:
    structure: float = 20.0
    liquidity: float = 20.0
    cisd: float = 20.0
    fvg: float = 15.0
    session: float = 10.0
    confidence: float = 15.0


class OpportunityQualificationEngine:
    """Combine signal factors into a research quality score."""

    def __init__(self, weights: QualificationWeights | None = None) -> None:
        self.weights = weights or QualificationWeights()
        self.structure = StructureScoreEngine()
        self.liquidity = LiquidityScoreEngine()
        self.cisd = CISDScoreEngine()
        self.fvg = FVGScoreEngine()
        self.session = SessionScoreEngine()

    def qualify(self, signal: dict) -> QualifiedOpportunity:
        structure = self.structure.score(signal)
        liquidity = self.liquidity.score(signal)
        cisd = self.cisd.score(signal)
        fvg = self.fvg.score(signal)
        session = self.session.score(signal)
        confidence = float(signal.get("confidence", {}).get("score", 0.0) or 0.0)
        score = self._weighted_score(structure, liquidity, cisd, fvg, session, confidence)
        strengths, weaknesses = self._strengths_and_weaknesses(
            [structure, liquidity, cisd, fvg, session]
        )
        state = self.state(score)
        return QualifiedOpportunity(
            opportunity_id=f"{signal.get('asset', 'ASSET')}:{signal.get('timestamp')}",
            asset=str(signal.get("asset", "")),
            classification=str(signal.get("classification_ar", "")),
            confidence=confidence,
            qualification_score=score,
            timestamp=_parse_timestamp(str(signal.get("timestamp"))),
            structure_score=structure.score,
            liquidity_score=liquidity.score,
            cisd_score=cisd.score,
            fvg_score=fvg.score,
            session_score=session.score,
            supporting_factors=list(signal.get("supporting_factors", [])) + strengths,
            rejection_factors=list(signal.get("rejection_factors", [])) + weaknesses,
            qualification_state=state,
            explanation=self.explanation(state, score),
            strengths=strengths,
            weaknesses=weaknesses,
            metadata={
                "research_only": True,
                "not_recommendation": True,
                "not_execution": True,
            },
        )

    def state(self, score: float) -> str:
        if score >= 90:
            return "مؤهلة جدا"
        if score >= 75:
            return "مؤهلة"
        if score >= 60:
            return "متوسطة"
        if score >= 40:
            return "ضعيفة"
        return "مرفوضة"

    def explanation(self, state: str, score: float) -> str:
        return f"حالة التأهيل {state} بناء على درجة جودة بحثية {score:.2f}."

    def _weighted_score(
        self,
        structure: ScoreBreakdown,
        liquidity: ScoreBreakdown,
        cisd: ScoreBreakdown,
        fvg: ScoreBreakdown,
        session: ScoreBreakdown,
        confidence: float,
    ) -> float:
        total = (
            structure.score * self.weights.structure
            + liquidity.score * self.weights.liquidity
            + cisd.score * self.weights.cisd
            + fvg.score * self.weights.fvg
            + session.score * self.weights.session
            + confidence * self.weights.confidence
        )
        return round(total / 100.0, 2)

    def _strengths_and_weaknesses(
        self,
        scores: list[ScoreBreakdown],
    ) -> tuple[list[str], list[str]]:
        strengths = []
        weaknesses = []
        for score in scores:
            strengths.extend(score.strengths)
            weaknesses.extend(score.weaknesses)
        return strengths, weaknesses


def _parse_timestamp(value: str):
    from datetime import datetime

    return datetime.fromisoformat(value)
