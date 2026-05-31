"""Typed models for platform certification outputs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.platform_certification.schemas import SCHEMA_VERSION

GENERATED_AT = "deterministic-final-research-platform-certification"


@dataclass(frozen=True)
class CertificationDomainResult:
    """One certification domain result."""

    domain_id: str
    label_ar: str
    score: float
    status: str
    diagnostics: list[dict[str, Any]]
    recommendations: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "domain_id": self.domain_id,
            "label_ar": self.label_ar,
            "score": self.score,
            "status": self.status,
            "diagnostics": self.diagnostics,
            "recommendations": self.recommendations,
        }


@dataclass(frozen=True)
class PlatformCertificationResult:
    """Final platform certification package."""

    certification_id: str
    generated_at: str
    final_platform_score: float
    certification_state: str
    research_maturity_level: str
    maturity_score: float
    domain_scores: list[CertificationDomainResult]
    diagnostics: list[dict[str, Any]]
    recommendations: list[str]
    safety_boundary: dict[str, bool]
    schema_version: str = SCHEMA_VERSION
    research_only: bool = True
    local_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "certification_id": self.certification_id,
            "generated_at": self.generated_at,
            "final_platform_score": self.final_platform_score,
            "certification_state": self.certification_state,
            "research_maturity_level": self.research_maturity_level,
            "maturity_score": self.maturity_score,
            "domain_scores": [domain.to_dict() for domain in self.domain_scores],
            "diagnostics": self.diagnostics,
            "recommendations": self.recommendations,
            "safety_boundary": self.safety_boundary,
            "schema_version": self.schema_version,
            "research_only": self.research_only,
            "local_only": self.local_only,
        }
