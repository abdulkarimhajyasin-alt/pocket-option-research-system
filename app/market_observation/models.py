"""Typed models for the canonical passive market observation source."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class MarketObservationRecord:
    """One normalized passive observation from an existing local source."""

    observation_id: str
    source_type: str
    source_name: str
    timestamp: str
    asset_count: float
    payout_count: float
    session_count: float
    symbol_count: float
    market_data_score: float
    visibility_score: float
    quality_score: float
    confidence_score: float
    freshness_score: float
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "source_type": self.source_type,
            "source_name": self.source_name,
            "timestamp": self.timestamp,
            "asset_count": self.asset_count,
            "payout_count": self.payout_count,
            "session_count": self.session_count,
            "symbol_count": self.symbol_count,
            "market_data_score": self.market_data_score,
            "visibility_score": self.visibility_score,
            "quality_score": self.quality_score,
            "confidence_score": self.confidence_score,
            "freshness_score": self.freshness_score,
            "payload": self.payload,
            "research_only": True,
            "observation_only": True,
        }


@dataclass(frozen=True)
class MarketObservationValidation:
    """Validation result for canonical observation inputs."""

    score: float
    source_count: int
    normalized_count: int
    completeness: float
    consistency: float
    integrity: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "source_count": self.source_count,
            "normalized_count": self.normalized_count,
            "completeness": self.completeness,
            "consistency": self.consistency,
            "integrity": self.integrity,
        }


@dataclass(frozen=True)
class MarketObservationAggregate:
    """Canonical aggregate consumed by research dashboards and reports."""

    score: float
    state: str
    explanation: str
    coverage_score: float
    quality_score: float
    confidence_score: float
    visibility_score: float
    freshness_score: float
    consistency_score: float
    asset_count: float
    payout_count: float
    session_count: float
    symbol_count: float
    source_distribution: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "state": self.state,
            "explanation": self.explanation,
            "coverage_score": self.coverage_score,
            "quality_score": self.quality_score,
            "confidence_score": self.confidence_score,
            "visibility_score": self.visibility_score,
            "freshness_score": self.freshness_score,
            "consistency_score": self.consistency_score,
            "asset_count": self.asset_count,
            "payout_count": self.payout_count,
            "session_count": self.session_count,
            "symbol_count": self.symbol_count,
            "source_distribution": self.source_distribution,
        }


@dataclass(frozen=True)
class MarketObservationDiagnostic:
    """Arabic diagnostic finding for market observation quality."""

    name: str
    severity: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "severity": self.severity, "detail": self.detail}


@dataclass(frozen=True)
class MarketObservationResult:
    """Complete canonical market observation result."""

    timestamp: datetime
    observations: tuple[MarketObservationRecord, ...]
    validation: MarketObservationValidation
    aggregate: MarketObservationAggregate
    diagnostics: tuple[MarketObservationDiagnostic, ...]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "observations": [item.to_dict() for item in self.observations],
            "validation": self.validation.to_dict(),
            "aggregate": self.aggregate.to_dict(),
            "diagnostics": [item.to_dict() for item in self.diagnostics],
            "metadata": self.metadata,
            "research_only": True,
            "observation_only": True,
            "canonical_market_observation": True,
            "not_execution": True,
            "not_order_placement": True,
            "not_account_login": True,
            "not_broker_authentication": True,
            "not_credential_handling": True,
            "not_browser_automation": True,
            "not_broker_control": True,
        }
