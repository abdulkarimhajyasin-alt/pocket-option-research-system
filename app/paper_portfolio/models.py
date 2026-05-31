"""Typed models for paper-only portfolio governance."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


PASS = "PASS"
WARNING = "WARNING"
FAIL = "FAIL"


@dataclass(frozen=True)
class PaperPortfolio:
    """Aggregated paper-only portfolio state."""

    portfolio_id: str
    created_at: str
    total_orders: int
    active_orders: int
    wins: int
    losses: int
    breakeven: int
    win_rate: float
    drawdown: float
    stability_score: float
    health_score: float
    risk_score: float
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "portfolio_id": self.portfolio_id,
            "created_at": self.created_at,
            "total_orders": self.total_orders,
            "active_orders": self.active_orders,
            "wins": self.wins,
            "losses": self.losses,
            "breakeven": self.breakeven,
            "win_rate": self.win_rate,
            "drawdown": self.drawdown,
            "stability_score": self.stability_score,
            "health_score": self.health_score,
            "risk_score": self.risk_score,
            "metadata": self.metadata,
            "paper_only": True,
            "research_only": True,
            "not_real_money": True,
            "not_real_execution": True,
        }


@dataclass(frozen=True)
class PortfolioGateResult:
    """Governance or limit result."""

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
class PortfolioDiagnostic:
    """Arabic portfolio diagnostic."""

    name: str
    severity: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "severity": self.severity, "detail": self.detail}


@dataclass(frozen=True)
class PortfolioRecommendation:
    """Arabic portfolio recommendation."""

    title: str
    priority: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {"title": self.title, "priority": self.priority, "reason": self.reason}


@dataclass(frozen=True)
class PaperPortfolioRun:
    """Complete paper-only portfolio governance run."""

    timestamp: datetime
    portfolio: PaperPortfolio
    exposure: dict[str, Any]
    drawdown: dict[str, Any]
    governance: tuple[PortfolioGateResult, ...]
    limits: tuple[PortfolioGateResult, ...]
    analytics: dict[str, Any]
    diagnostics: tuple[PortfolioDiagnostic, ...]
    recommendations: tuple[PortfolioRecommendation, ...]
    score: float
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "portfolio": self.portfolio.to_dict(),
            "exposure": self.exposure,
            "drawdown": self.drawdown,
            "governance": [item.to_dict() for item in self.governance],
            "limits": [item.to_dict() for item in self.limits],
            "analytics": self.analytics,
            "diagnostics": [item.to_dict() for item in self.diagnostics],
            "recommendations": [item.to_dict() for item in self.recommendations],
            "score": self.score,
            "metadata": self.metadata,
            "paper_only": True,
            "research_only": True,
            "not_real_execution": True,
            "not_real_money": True,
            "not_broker_access": True,
            "not_browser_automation": True,
        }
