"""Typed models for external integration safety boundary."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


PASS = "PASS"
WARNING = "WARNING"
FAIL = "FAIL"

BOUNDARY_FULLY_PROTECTED = "محمية بالكامل"
BOUNDARY_CONDITIONALLY_PROTECTED = "محمية بشروط"
BOUNDARY_NEEDS_REVIEW = "تحتاج مراجعة"
BOUNDARY_UNSAFE = "غير آمنة"

ALLOWED_CAPABILITIES = (
    "local file reading",
    "local report reading",
    "passive snapshot parsing",
    "passive observation modeling",
    "local replay",
    "local paper simulation",
    "local diagnostics",
    "local reporting",
)

FORBIDDEN_CAPABILITIES = (
    "broker connection",
    "broker APIs",
    "account login",
    "authentication",
    "credential storage",
    "browser automation",
    "button clicking",
    "DOM control",
    "trade placement",
    "order placement",
    "real execution",
    "money handling",
    "account changes",
    "withdrawals",
    "deposits",
    "external trading actions",
)


@dataclass(frozen=True)
class IntegrationSafetyPolicy:
    """Safety policy for future external integration work."""

    policy_id: str
    generated_at: str
    allowed_capabilities: tuple[str, ...]
    forbidden_capabilities: tuple[str, ...]
    boundary_status: str
    safety_score: float
    compliance_score: float
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "generated_at": self.generated_at,
            "allowed_capabilities": list(self.allowed_capabilities),
            "forbidden_capabilities": list(self.forbidden_capabilities),
            "boundary_status": self.boundary_status,
            "safety_score": self.safety_score,
            "compliance_score": self.compliance_score,
            "metadata": self.metadata,
            "safety_boundary_only": True,
            "readiness_only": True,
            "research_only": True,
            "not_real_execution": True,
            "not_broker_access": True,
            "not_browser_automation": True,
            "not_external_execution_adapter": True,
        }


@dataclass(frozen=True)
class SafetyDiagnostic:
    """Arabic diagnostic for integration safety boundary."""

    name: str
    severity: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "severity": self.severity, "detail": self.detail}


@dataclass(frozen=True)
class SafetyRecommendation:
    """Arabic safety recommendation."""

    title: str
    priority: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {"title": self.title, "priority": self.priority, "reason": self.reason}


@dataclass(frozen=True)
class IntegrationSafetyRun:
    """Complete integration safety boundary run."""

    timestamp: datetime
    policy: IntegrationSafetyPolicy
    boundary: dict[str, Any]
    permissions: dict[str, Any]
    restrictions: dict[str, Any]
    compliance: dict[str, Any]
    audit: dict[str, Any]
    analytics: dict[str, Any]
    diagnostics: tuple[SafetyDiagnostic, ...]
    recommendations: tuple[SafetyRecommendation, ...]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "policy": self.policy.to_dict(),
            "boundary": self.boundary,
            "permissions": self.permissions,
            "restrictions": self.restrictions,
            "compliance": self.compliance,
            "audit": self.audit,
            "analytics": self.analytics,
            "diagnostics": [item.to_dict() for item in self.diagnostics],
            "recommendations": [item.to_dict() for item in self.recommendations],
            "metadata": self.metadata,
            "safety_boundary_only": True,
            "readiness_only": True,
            "research_only": True,
            "not_execution": True,
            "not_real_execution": True,
            "not_order_placement": True,
            "not_real_order_placement": True,
            "not_broker_access": True,
            "not_broker_api": True,
            "not_browser_automation": True,
            "not_authentication": True,
            "not_credential_handling": True,
            "not_real_money": True,
            "not_position_management": True,
            "not_live_trading": True,
            "not_external_execution_adapter": True,
            "not_trading_automation": True,
        }
