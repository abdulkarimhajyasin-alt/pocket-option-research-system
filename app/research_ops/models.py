"""Typed models for research operations control center."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class ResearchHealth:
    score: float
    classification: str
    explanation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "classification": self.classification,
            "explanation": self.explanation,
            "research_only": True,
        }


@dataclass(frozen=True)
class StrategyStatus:
    readiness_score: float
    readiness_state: str
    passed_gates: int
    warnings: int
    failures: int
    research_quality: float
    confidence_stability: float
    lifecycle_quality: float

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class OpportunityStatus:
    top_opportunity: str
    strongest_confluence: float
    strongest_alignment: float
    strongest_session: str
    strongest_liquidity: float
    opportunity_count: int

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class RiskAssessment:
    severity: str
    risks: list[str]
    score: float

    def to_dict(self) -> dict[str, Any]:
        return {"severity": self.severity, "risks": self.risks, "score": self.score}


@dataclass(frozen=True)
class ResearchAlert:
    title: str
    severity: str
    explanation: str
    recommendation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "severity": self.severity,
            "explanation": self.explanation,
            "recommendation": self.recommendation,
        }


@dataclass(frozen=True)
class PriorityRecommendation:
    title: str
    priority: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {"title": self.title, "priority": self.priority, "reason": self.reason}


@dataclass(frozen=True)
class NextAction:
    action: str
    reason: str
    priority: str

    def to_dict(self) -> dict[str, Any]:
        return {"action": self.action, "reason": self.reason, "priority": self.priority}


@dataclass(frozen=True)
class ExecutiveSummary:
    best_opportunity: str
    readiness_status: str
    research_health: ResearchHealth
    active_alerts: int
    strategic_recommendation: str
    next_action: NextAction
    top_risk: str
    top_strength: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "best_opportunity": self.best_opportunity,
            "readiness_status": self.readiness_status,
            "research_health": self.research_health.to_dict(),
            "active_alerts": self.active_alerts,
            "strategic_recommendation": self.strategic_recommendation,
            "next_action": self.next_action.to_dict(),
            "top_risk": self.top_risk,
            "top_strength": self.top_strength,
            "research_only": True,
        }


@dataclass(frozen=True)
class ResearchOperationsResult:
    timestamp: datetime
    executive_summary: ExecutiveSummary
    strategy_status: StrategyStatus
    opportunity_status: OpportunityStatus
    risk_assessment: RiskAssessment
    alerts: tuple[ResearchAlert, ...]
    recommendations: tuple[PriorityRecommendation, ...]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "executive_summary": self.executive_summary.to_dict(),
            "strategy_status": self.strategy_status.to_dict(),
            "opportunity_status": self.opportunity_status.to_dict(),
            "risk_assessment": self.risk_assessment.to_dict(),
            "alerts": [item.to_dict() for item in self.alerts],
            "recommendations": [item.to_dict() for item in self.recommendations],
            "metadata": self.metadata,
            "research_only": True,
            "not_execution": True,
            "not_investment_advice": True,
        }
