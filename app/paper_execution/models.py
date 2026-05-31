"""Typed models for paper-only execution simulation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


DIRECTION_CALL = "CALL"
DIRECTION_PUT = "PUT"
DIRECTION_NO_TRADE = "NO_TRADE"

STATUS_CREATED = "CREATED"
STATUS_ACCEPTED = "ACCEPTED"
STATUS_REJECTED = "REJECTED"
STATUS_ACTIVE = "ACTIVE"
STATUS_EXPIRED = "EXPIRED"
STATUS_WIN = "WIN"
STATUS_LOSS = "LOSS"
STATUS_BREAKEVEN = "BREAKEVEN"
STATUS_CANCELLED = "CANCELLED"
STATUS_UNRESOLVED = "UNRESOLVED"

RISK_PASS = "PASS"
RISK_WARNING = "WARNING"
RISK_FAIL = "FAIL"

STATUS_ARABIC = {
    STATUS_CREATED: "تم الإنشاء",
    STATUS_ACCEPTED: "مقبول",
    STATUS_REJECTED: "مرفوض",
    STATUS_ACTIVE: "نشط",
    STATUS_EXPIRED: "منتهي",
    STATUS_WIN: "رابح",
    STATUS_LOSS: "خاسر",
    STATUS_BREAKEVEN: "تعادل",
    STATUS_CANCELLED: "ملغى",
    STATUS_UNRESOLVED: "غير محسوم",
}


@dataclass(frozen=True)
class PaperOrder:
    """One local paper-only order derived from an execution-readiness candidate."""

    order_id: str
    candidate_id: str
    signal_id: str
    asset: str
    direction: str
    confidence: float
    readiness_score: float
    qualification_state: str
    created_at: str
    expiry: str
    status: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "order_id": self.order_id,
            "candidate_id": self.candidate_id,
            "signal_id": self.signal_id,
            "asset": self.asset,
            "direction": self.direction,
            "confidence": self.confidence,
            "readiness_score": self.readiness_score,
            "qualification_state": self.qualification_state,
            "created_at": self.created_at,
            "expiry": self.expiry,
            "status": self.status,
            "status_label": STATUS_ARABIC.get(self.status, self.status),
            "metadata": self.metadata,
            "paper_only": True,
            "research_only": True,
            "not_real_execution": True,
            "not_real_order_placement": True,
        }


@dataclass(frozen=True)
class PaperLifecycleEvent:
    """One paper order lifecycle transition."""

    order_id: str
    candidate_id: str
    from_status: str
    to_status: str
    timestamp: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {
            "order_id": self.order_id,
            "candidate_id": self.candidate_id,
            "from_status": self.from_status,
            "to_status": self.to_status,
            "to_status_label": STATUS_ARABIC.get(self.to_status, self.to_status),
            "timestamp": self.timestamp,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class PaperResult:
    """Paper-only simulated outcome for one order."""

    order_id: str
    candidate_id: str
    signal_id: str
    outcome: str
    simulated_return: float
    evaluated_at: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "order_id": self.order_id,
            "candidate_id": self.candidate_id,
            "signal_id": self.signal_id,
            "outcome": self.outcome,
            "outcome_label": STATUS_ARABIC.get(self.outcome, self.outcome),
            "simulated_return": self.simulated_return,
            "evaluated_at": self.evaluated_at,
            "reason": self.reason,
            "paper_only": True,
            "research_only": True,
        }


@dataclass(frozen=True)
class PaperRiskGate:
    """Paper-only risk gate result."""

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
class PaperExecutionDiagnostic:
    """Arabic paper execution diagnostic."""

    name: str
    severity: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "severity": self.severity, "detail": self.detail}


@dataclass(frozen=True)
class PaperExecutionRecommendation:
    """Arabic paper execution recommendation."""

    title: str
    priority: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {"title": self.title, "priority": self.priority, "reason": self.reason}


@dataclass(frozen=True)
class PaperExecutionRun:
    """Complete paper-only execution run."""

    timestamp: datetime
    orders: tuple[PaperOrder, ...]
    lifecycle: tuple[PaperLifecycleEvent, ...]
    results: tuple[PaperResult, ...]
    risk_gates: tuple[PaperRiskGate, ...]
    analytics: dict[str, Any]
    diagnostics: tuple[PaperExecutionDiagnostic, ...]
    recommendations: tuple[PaperExecutionRecommendation, ...]
    score: float
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "orders": [item.to_dict() for item in self.orders],
            "lifecycle": [item.to_dict() for item in self.lifecycle],
            "results": [item.to_dict() for item in self.results],
            "risk_gates": [item.to_dict() for item in self.risk_gates],
            "analytics": self.analytics,
            "diagnostics": [item.to_dict() for item in self.diagnostics],
            "recommendations": [item.to_dict() for item in self.recommendations],
            "score": self.score,
            "metadata": self.metadata,
            "paper_only": True,
            "research_only": True,
            "not_real_execution": True,
            "not_real_order_placement": True,
            "not_broker_access": True,
            "not_browser_automation": True,
        }
