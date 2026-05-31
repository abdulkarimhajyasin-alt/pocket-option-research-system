"""Typed models for paper-only control center."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


PASS = "PASS"
WARNING = "WARNING"
FAIL = "FAIL"

DECISION_CONTINUE = "متابعة التشغيل الورقي"
DECISION_REVIEW = "مراجعة مطلوبة"
DECISION_PAUSE = "إيقاف التشغيل الورقي"


@dataclass(frozen=True)
class PaperControlCenter:
    """Executive paper-only control center state."""

    control_id: str
    generated_at: str
    portfolio_health: float
    portfolio_stability: float
    execution_status: str
    readiness_status: str
    governance_status: str
    risk_status: str
    recommendation_count: int
    warning_count: int
    overall_score: float
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "control_id": self.control_id,
            "generated_at": self.generated_at,
            "portfolio_health": self.portfolio_health,
            "portfolio_stability": self.portfolio_stability,
            "execution_status": self.execution_status,
            "readiness_status": self.readiness_status,
            "governance_status": self.governance_status,
            "risk_status": self.risk_status,
            "recommendation_count": self.recommendation_count,
            "warning_count": self.warning_count,
            "overall_score": self.overall_score,
            "metadata": self.metadata,
            "paper_only": True,
            "research_only": True,
            "not_real_execution": True,
            "not_broker_access": True,
        }


@dataclass(frozen=True)
class ControlGate:
    """One paper control governance result."""

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
class ControlDiagnostic:
    """Arabic diagnostic for the paper control center."""

    name: str
    severity: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "severity": self.severity, "detail": self.detail}


@dataclass(frozen=True)
class ControlRecommendation:
    """Arabic recommendation for the paper control center."""

    title: str
    priority: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {"title": self.title, "priority": self.priority, "reason": self.reason}


@dataclass(frozen=True)
class PaperControlCenterRun:
    """Complete paper-only control center run."""

    timestamp: datetime
    control: PaperControlCenter
    health: dict[str, Any]
    monitoring: dict[str, Any]
    governance: tuple[ControlGate, ...]
    decision: dict[str, Any]
    analytics: dict[str, Any]
    diagnostics: tuple[ControlDiagnostic, ...]
    recommendations: tuple[ControlRecommendation, ...]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "control": self.control.to_dict(),
            "health": self.health,
            "monitoring": self.monitoring,
            "governance": [item.to_dict() for item in self.governance],
            "decision": self.decision,
            "analytics": self.analytics,
            "diagnostics": [item.to_dict() for item in self.diagnostics],
            "recommendations": [item.to_dict() for item in self.recommendations],
            "metadata": self.metadata,
            "paper_only": True,
            "research_only": True,
            "recommendation_only": True,
            "not_real_execution": True,
            "not_real_order_placement": True,
            "not_broker_access": True,
            "not_browser_automation": True,
            "not_real_money": True,
            "not_trading_automation": True,
        }
