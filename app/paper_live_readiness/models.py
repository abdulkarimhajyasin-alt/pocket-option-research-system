"""Typed models for paper-to-live readiness assessment."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


PASS = "PASS"
WARNING = "WARNING"
FAIL = "FAIL"

STATE_ADVANCED_OBSERVATION = "جاهزة لمرحلة مراقبة متقدمة"
STATE_STRICT_CONDITIONS = "جاهزة بشروط صارمة"
STATE_LIMITED_IMPROVEMENT = "تحتاج تحسين محدود"
STATE_MAJOR_IMPROVEMENT = "تحتاج تحسين كبير"
STATE_NOT_QUALIFIED = "غير مؤهلة"


@dataclass(frozen=True)
class PaperToLiveReadiness:
    """Executive readiness-only assessment state."""

    readiness_id: str
    generated_at: str
    paper_health: float
    paper_stability: float
    paper_governance: float
    execution_readiness: float
    observation_readiness: float
    certification_score: float
    safety_score: float
    maturity_score: float
    overall_score: float
    readiness_state: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "readiness_id": self.readiness_id,
            "generated_at": self.generated_at,
            "paper_health": self.paper_health,
            "paper_stability": self.paper_stability,
            "paper_governance": self.paper_governance,
            "execution_readiness": self.execution_readiness,
            "observation_readiness": self.observation_readiness,
            "certification_score": self.certification_score,
            "safety_score": self.safety_score,
            "maturity_score": self.maturity_score,
            "overall_score": self.overall_score,
            "readiness_state": self.readiness_state,
            "metadata": self.metadata,
            "readiness_only": True,
            "paper_only": True,
            "research_only": True,
            "not_real_execution": True,
            "not_live_trading": True,
            "not_broker_access": True,
        }


@dataclass(frozen=True)
class ReadinessGate:
    """One paper-to-live readiness gate result."""

    name: str
    arabic_label: str
    status: str
    score: float
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "arabic_label": self.arabic_label,
            "status": self.status,
            "score": self.score,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class ReadinessDiagnostic:
    """Arabic diagnostic item for readiness gate."""

    name: str
    severity: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "severity": self.severity, "detail": self.detail}


@dataclass(frozen=True)
class ReadinessRecommendation:
    """Arabic recommendation item for readiness gate."""

    title: str
    priority: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {"title": self.title, "priority": self.priority, "reason": self.reason}


@dataclass(frozen=True)
class PaperToLiveReadinessRun:
    """Complete readiness-only run."""

    timestamp: datetime
    readiness: PaperToLiveReadiness
    gates: tuple[ReadinessGate, ...]
    safety: dict[str, Any]
    maturity: dict[str, Any]
    stability: dict[str, Any]
    analytics: dict[str, Any]
    diagnostics: tuple[ReadinessDiagnostic, ...]
    recommendations: tuple[ReadinessRecommendation, ...]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "readiness": self.readiness.to_dict(),
            "gates": [item.to_dict() for item in self.gates],
            "safety": self.safety,
            "maturity": self.maturity,
            "stability": self.stability,
            "analytics": self.analytics,
            "diagnostics": [item.to_dict() for item in self.diagnostics],
            "recommendations": [item.to_dict() for item in self.recommendations],
            "metadata": self.metadata,
            "readiness_only": True,
            "paper_only": True,
            "research_only": True,
            "not_execution": True,
            "not_real_execution": True,
            "not_order_placement": True,
            "not_real_order_placement": True,
            "not_live_trading": True,
            "not_broker_access": True,
            "not_browser_automation": True,
            "not_authentication": True,
            "not_credential_handling": True,
            "not_real_money": True,
            "not_trading_automation": True,
        }
