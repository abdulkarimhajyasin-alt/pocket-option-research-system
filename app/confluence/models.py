"""Typed models for unified confluence research decisions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class FactorScore:
    """Single independently testable confluence factor score."""

    name: str
    score: float
    explanation: str
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "score": self.score,
            "explanation": self.explanation,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "warnings": self.warnings,
            "metrics": self.metrics,
        }


@dataclass(frozen=True)
class SignalFactorScore(FactorScore):
    """Signal intelligence factor score."""


@dataclass(frozen=True)
class PerformanceFactorScore(FactorScore):
    """Historical research performance factor score."""


@dataclass(frozen=True)
class OpportunityFactorScore(FactorScore):
    """Opportunity qualification factor score."""


@dataclass(frozen=True)
class TimeframeFactorScore(FactorScore):
    """Multi-timeframe confirmation factor score."""


@dataclass(frozen=True)
class SessionFactorScore(FactorScore):
    """Session quality factor score."""


@dataclass(frozen=True)
class LiquidityFactorScore(FactorScore):
    """Liquidity context factor score."""


@dataclass(frozen=True)
class ConfluenceScore:
    """Unified confluence score, not a trading recommendation."""

    opportunity_id: str
    asset: str
    classification: str
    session: str
    timestamp: datetime
    score: float
    state: str
    explanation: str
    factors: tuple[FactorScore, ...]
    strengths: list[str]
    weaknesses: list[str]
    warnings: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "opportunity_id": self.opportunity_id,
            "asset": self.asset,
            "classification": self.classification,
            "session": self.session,
            "timestamp": self.timestamp.isoformat(),
            "score": self.score,
            "state": self.state,
            "explanation": self.explanation,
            "factors": [factor.to_dict() for factor in self.factors],
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "warnings": self.warnings,
            "metadata": self.metadata,
            "research_only": True,
        }


@dataclass(frozen=True)
class ResearchDecision:
    """Final research decision view with explicit safety framing."""

    opportunity_id: str
    asset: str
    classification: str
    final_decision: str
    confluence_score: float
    confidence_level: str
    acceptance_reasons: list[str]
    rejection_reasons: list[str]
    risk_factors: list[str]
    readiness: str
    confluence: ConfluenceScore

    def to_dict(self) -> dict[str, Any]:
        return {
            "opportunity_id": self.opportunity_id,
            "asset": self.asset,
            "classification": self.classification,
            "final_decision": self.final_decision,
            "confluence_score": self.confluence_score,
            "confidence_level": self.confidence_level,
            "acceptance_reasons": self.acceptance_reasons,
            "rejection_reasons": self.rejection_reasons,
            "risk_factors": self.risk_factors,
            "readiness": self.readiness,
            "confluence": self.confluence.to_dict(),
            "research_only": True,
            "not_execution": True,
            "not_investment_advice": True,
        }


@dataclass(frozen=True)
class ReadinessAssessment:
    """Research readiness assessment only."""

    score: float
    label: str
    reasons: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "label": self.label,
            "reasons": self.reasons,
            "research_only": True,
        }
