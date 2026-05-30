"""Typed models for qualified research opportunities."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class ScoreBreakdown:
    """Component score with Arabic explanation."""

    score: float
    explanation: str
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "explanation": self.explanation,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
        }


@dataclass(frozen=True)
class QualifiedOpportunity:
    """Research opportunity quality score, not a trading recommendation."""

    opportunity_id: str
    asset: str
    classification: str
    confidence: float
    qualification_score: float
    timestamp: datetime
    structure_score: float
    liquidity_score: float
    cisd_score: float
    fvg_score: float
    session_score: float
    supporting_factors: list[str]
    rejection_factors: list[str]
    qualification_state: str
    explanation: str
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "opportunity_id": self.opportunity_id,
            "asset": self.asset,
            "classification": self.classification,
            "confidence": self.confidence,
            "qualification_score": self.qualification_score,
            "timestamp": self.timestamp.isoformat(),
            "structure_score": self.structure_score,
            "liquidity_score": self.liquidity_score,
            "cisd_score": self.cisd_score,
            "fvg_score": self.fvg_score,
            "session_score": self.session_score,
            "supporting_factors": self.supporting_factors,
            "rejection_factors": self.rejection_factors,
            "qualification_state": self.qualification_state,
            "explanation": self.explanation,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "metadata": self.metadata,
            "research_only": True,
        }


@dataclass(frozen=True)
class OpportunityRanking:
    """Ranked opportunity view."""

    rank: int
    opportunity: QualifiedOpportunity
    reasoning: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "rank": self.rank,
            "score": self.opportunity.qualification_score,
            "reasoning": self.reasoning,
            "opportunity": self.opportunity.to_dict(),
            "research_only": True,
        }
