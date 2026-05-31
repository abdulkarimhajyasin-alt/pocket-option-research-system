"""Typed models for production research architecture audit."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


CERT_FULLY_READY = "جاهزة بالكامل"
CERT_CONDITIONALLY_READY = "جاهزة بشروط"
CERT_NEEDS_REVIEW = "تحتاج مراجعة"
CERT_NEEDS_RESTRUCTURE = "تحتاج إعادة هيكلة"


@dataclass(frozen=True)
class ProductionResearchCertification:
    """Final production research certification state."""

    certification_id: str
    generated_at: str
    architecture_score: float
    consistency_score: float
    dependency_score: float
    performance_score: float
    safety_score: float
    overall_score: float
    certification_state: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "certification_id": self.certification_id,
            "generated_at": self.generated_at,
            "architecture_score": self.architecture_score,
            "consistency_score": self.consistency_score,
            "dependency_score": self.dependency_score,
            "performance_score": self.performance_score,
            "safety_score": self.safety_score,
            "overall_score": self.overall_score,
            "certification_state": self.certification_state,
            "metadata": self.metadata,
            "architecture_audit_only": True,
            "hardening_only": True,
            "research_only": True,
            "not_real_execution": True,
            "not_broker_access": True,
            "not_browser_automation": True,
        }


@dataclass(frozen=True)
class ArchitectureDiagnostic:
    """Arabic diagnostic for production architecture audit."""

    name: str
    severity: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "severity": self.severity, "detail": self.detail}


@dataclass(frozen=True)
class ArchitectureRecommendation:
    """Arabic remediation recommendation."""

    title: str
    priority: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {"title": self.title, "priority": self.priority, "reason": self.reason}


@dataclass(frozen=True)
class ArchitectureAuditRun:
    """Complete architecture audit run."""

    timestamp: datetime
    certification: ProductionResearchCertification
    architecture: dict[str, Any]
    consistency: dict[str, Any]
    dependency: dict[str, Any]
    performance: dict[str, Any]
    safety: dict[str, Any]
    analytics: dict[str, Any]
    diagnostics: tuple[ArchitectureDiagnostic, ...]
    recommendations: tuple[ArchitectureRecommendation, ...]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "certification": self.certification.to_dict(),
            "architecture": self.architecture,
            "consistency": self.consistency,
            "dependency": self.dependency,
            "performance": self.performance,
            "safety": self.safety,
            "analytics": self.analytics,
            "diagnostics": [item.to_dict() for item in self.diagnostics],
            "recommendations": [item.to_dict() for item in self.recommendations],
            "metadata": self.metadata,
            "architecture_audit_only": True,
            "hardening_only": True,
            "research_only": True,
            "not_execution": True,
            "not_real_execution": True,
            "not_broker_access": True,
            "not_browser_automation": True,
            "not_authentication": True,
            "not_credential_handling": True,
            "not_live_trading": True,
            "not_external_execution_adapter": True,
            "not_trading_automation": True,
        }
